#!/usr/bin/env python3
"""
rcheck.py
MP3 copyright checker (AudioTag, AcoustID, AudD, ACRCloud)
"""

import os, sys, tempfile, subprocess, threading, requests, argparse, logging, time, json
from colorama import init as colorama_init, Fore, Style
import acoustid
from requests_toolbelt.multipart.encoder import MultipartEncoder, MultipartEncoderMonitor
from acrcloud.recognizer import ACRCloudRecognizer

# ----------------- AUTHOR INFO ----------------
AUTHOR = "Igor Brzezek"
AUTHOR_EMAIL = "igor.brzezek@gmail.com"
VERSION = 0.1alpha
DATE = 25.10.2025
# ----------------------------------------------

# ------------------ API KEYS ------------------
ACOUSTID_API_KEY = "YOUR_ACOUSTID_KEY"
AUDIOTAG_API_KEY = "YOUR_AUDIOTAG_KEY"
AUDD_API_KEY = "YOUR_AUDIOO_KEY"

# ACRCloud credentials
ACRCLOUD_CONFIG = {
    'host': 'identify-eu-west-1.acrcloud.com',
    'access_key': 'ACRCloud_ACCESS_KEY',
    'access_secret': 'ACRCloud_SECRET_KEY',
    'debug': False,
    'timeout': 10 # seconds
}

# ------------------ Constants ------------------
STATUS_WIDTH = 3
SERVICE_WIDTH = 40
BAR_WIDTH = 20

logger = logging.getLogger("rcheck25a")
logger.setLevel(logging.INFO)
colorama_init(autoreset=True)
_print_lock = threading.Lock()
_last_len_map = {}

# ------------------ Utility Functions ------------------
def overwrite_line(text):
    tid = threading.get_ident()
    with _print_lock:
        prev_len = _last_len_map.get(tid,0)
        sys.stdout.write("\r" + " "*prev_len + "\r")
        sys.stdout.write(text)
        sys.stdout.flush()
        _last_len_map[tid] = max(len(text), prev_len)

def finish_line():
    tid = threading.get_ident()
    with _print_lock:
        sys.stdout.write("\n")
        sys.stdout.flush()
        _last_len_map[tid] = 0

def format_size(bytes_size):
    return f"{bytes_size/(1024*1024):.1f} MB"

def color_text_file(text,status,color_enabled):
    if not color_enabled: return text
    if status=='C': return Fore.RED+text+Style.RESET_ALL
    if status=='F': return Fore.GREEN+text+Style.RESET_ALL
    if status=='U': return Fore.YELLOW+text+Style.RESET_ALL
    return text

def color_info(text,color_enabled):
    return (Fore.LIGHTBLUE_EX+text+Style.RESET_ALL) if color_enabled else text

def progress_bar(sent,total,width=BAR_WIDTH,char='#'):
    frac=float(sent)/total if total>0 else 1.0
    filled=int(round(frac*width))
    bar=char*filled+'-'*(width-filled)
    pct=int(frac*100)
    return f"[{bar}] {pct:3d}%"

# ------------------ Audio Processing (ffmpeg) ------------------
def get_audio_duration(file_path):
    command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', file_path]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError, FileNotFoundError):
        return 0

def trim_audio_ffmpeg(file_path, time_option, total_duration):
    if not total_duration: return None
    cut_seconds_str = ""
    if isinstance(time_option, str) and time_option.endswith('%'):
        try:
            pct = float(time_option[:-1]) / 100.0
            cut_seconds_str = str(total_duration * pct)
        except (ValueError, TypeError): pass
    else:
        try:
            cut_seconds_str = str(min(int(time_option), total_duration))
        except (ValueError, TypeError): pass
    if not cut_seconds_str: return None
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    base_command = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error']
    command = base_command + ['-i', file_path, '-t', cut_seconds_str, '-c', 'copy', tmp_path]
    try:
        subprocess.run(command, check=True)
        return tmp_path
    except subprocess.CalledProcessError:
        command[-2] = 'libmp3lame'
        try:
            subprocess.run(command, check=True)
            return tmp_path
        except subprocess.CalledProcessError as e:
            if os.path.exists(tmp_path): os.remove(tmp_path)
            return None

# ------------------ API Functions ------------------
fingerprint_cache = {}
def acoustid_lookup(fp_encoded,duration,debug=False):
    if not fp_encoded: return 'U','AcoustID'
    if fp_encoded in fingerprint_cache: return fingerprint_cache[fp_encoded]
    try:
        results=acoustid.lookup(ACOUSTID_API_KEY, fp_encoded, duration)
        for score,rid,title,artist in results:
            if score>=0.90:
                svc=f"AcoustID: {artist} - {title}"
                fingerprint_cache[fp_encoded]=('C',svc)
                return 'C',svc
    except acoustid.AcoustidError: pass
    fingerprint_cache[fp_encoded]=('U','AcoustID')
    return 'U','AcoustID'

def audiotag_identify_and_lookup(temp_path, time_len=None, debug=False, fullinfo=False, status_line_prefix=""):
    try:
        file_size = os.path.getsize(temp_path)
        def callback(monitor):
            bar = progress_bar(monitor.bytes_read, file_size)
            overwrite_line(f"{status_line_prefix} | sending {bar}")
        with open(temp_path, "rb") as f:
            fields = {
                'apikey': AUDIOTAG_API_KEY, 'action': 'identify',
                'file': (os.path.basename(temp_path), f, 'audio/mpeg')
            }
            encoder = MultipartEncoder(fields=fields)
            monitor = MultipartEncoderMonitor(encoder, callback)
            headers = {'Content-Type': monitor.content_type}
            try:
                resp = requests.post("https://audiotag.info/api", data=monitor, headers=headers, timeout=120)
            except requests.exceptions.RequestException:
                return 'U', 'AudioTag Network Error'
        if resp.status_code != 200: return 'U', 'AudioTag'
        j = resp.json()
        token = j.get('token')
        if not token: return 'U', 'AudioTag'
        for _ in range(30):
            resp2 = requests.post("https://audiotag.info/api", data={'apikey': AUDIOTAG_API_KEY, 'action': 'get_result', 'token': token}, timeout=30)
            if resp2.status_code == 200:
                r = resp2.json()
                result = r.get('result')
                if result == "found":
                    data_items = r.get("data", [])
                    if data_items:
                        track_info = data_items[0].get("tracks", [])
                        if track_info:
                            track = track_info[0]
                            title, artist = track[0], track[1]
                            confidence = data_items[0].get("confidence", "?")
                            svc = f"AudioTag: {artist} - {title}"
                            if fullinfo: svc += f" (confidence: {confidence}%)"
                            return 'C', svc
                    return 'U', 'AudioTag'
                elif result == "not found": return 'U', 'AudioTag'
            time.sleep(2)
        return 'U', 'AudioTag'
    except Exception: return 'U', 'AudioTag'

def audd_check(temp_path, debug=False, status_line_prefix=""):
    try:
        file_size = os.path.getsize(temp_path)
        def callback(monitor):
            bar = progress_bar(monitor.bytes_read, file_size)
            overwrite_line(f"{status_line_prefix} | sending {bar}")
        with open(temp_path,"rb") as f:
            encoder = MultipartEncoder(fields={
                "api_token": AUDD_API_KEY, "return": "spotify,apple_music,youtube",
                "file": (os.path.basename(temp_path), f, "audio/mpeg")
            })
            monitor = MultipartEncoderMonitor(encoder, callback)
            headers = {'Content-Type': monitor.content_type}
            try:
                resp=requests.post("https://api.audd.io/", data=monitor, headers=headers, timeout=120)
            except requests.exceptions.RequestException:
                return 'U', 'AudD Network Error'
        if resp.status_code!=200: return 'U','-'
        response_json = resp.json()
        if response_json.get("status") == "error":
            error_code = response_json.get("error", {}).get("error_code")
            if error_code == 902: return 'U', "AudD: API limit reached"
            return 'U', f"AudD Error {error_code}"
        r=response_json.get('result')
        if not r: return 'U','-'
        svcs=[s.capitalize() for s in ["spotify","youtube","apple_music"] if r.get(s)]
        status='C' if svcs else 'F'
        service=", ".join(svcs) if svcs else "-"
        return status,service
    except Exception: return 'U','-'

def acr_recognize(temp_path, debug=False, status_line_prefix=""):
    try:
        overwrite_line(f"{status_line_prefix} | Recognizing with ACRCloud...")
        re = ACRCloudRecognizer(ACRCLOUD_CONFIG)
        result_json = re.recognize_by_file(temp_path, 0)
        result = json.loads(result_json)
        if result['status']['msg'] == 'Success':
            meta = result['metadata']['music'][0]
            title = meta['title']
            artists = ', '.join([a['name'] for a in meta['artists']])
            return 'C', f"ACRCloud: {artists} - {title}"
        else:
            return 'U', f"ACRCloud: {result['status']['msg']}"
    except Exception as e:
        return 'U', f"ACRCloud Error: {e}"

# ------------------ File processing ------------------
def process_file(file_path, method, time_option, color_enabled, debug=False, fullinfo=False):
    fname=os.path.basename(file_path)
    full_size=os.path.getsize(file_path)
    full_size_str=format_size(full_size)
    total_seconds = get_audio_duration(file_path)
    total_time_str = f"{int(total_seconds//60)}:{int(total_seconds%60):02d}" if total_seconds > 0 else "?:??"
    overwrite_line(f"{fname} | size: {full_size_str} | time: {total_time_str} | preparing...")
    temp_file=file_path
    status_line_prefix = f"{fname} | size: {full_size_str} | time: {total_time_str}"
    if time_option:
        try:
            overwrite_line(f"{status_line_prefix} | Creating temp file...")
            trimmed_path = trim_audio_ffmpeg(file_path, time_option, total_seconds)
            if trimmed_path and os.path.exists(trimmed_path):
                temp_file = trimmed_path
        except Exception: pass
    cut_size=os.path.getsize(temp_file)
    cut_size_str=format_size(cut_size)
    status_line_prefix = f"{fname} | size: {full_size_str} | time: {total_time_str} | cut block: {cut_size_str}"
    status,service='U','-'
    try:
        if method=='acoustid':
            overwrite_line(f"{status_line_prefix} | Fingerprinting...")
            duration,fp=acoustid.fingerprint_file(temp_file)
            overwrite_line(f"{status_line_prefix} | Looking up fingerprint...")
            status,service=acoustid_lookup(fp,duration,debug)
        elif method=='audiotag':
            status,service=audiotag_identify_and_lookup(temp_file,time_option,debug,fullinfo, status_line_prefix)
        elif method=='acr':
            status,service=acr_recognize(temp_file,debug,status_line_prefix)
        else: # audioo
            status,service=audd_check(temp_file,debug, status_line_prefix)
    except Exception:
        status,service='U','-'
    if temp_file!=file_path:
        try: os.remove(temp_file)
        except: pass
    final_line=f"{color_info(status.ljust(STATUS_WIDTH),color_enabled)} | {color_info(service.ljust(SERVICE_WIDTH),color_enabled)} | {color_text_file(fname,status,color_enabled)}"
    overwrite_line(final_line)
    finish_line()
    return {"file":fname,"status":status,"service":service}

# ------------------ Main ------------------
def main():
    parser=argparse.ArgumentParser(description="Check MP3 files for copyright using various services.")
    parser.add_argument("-i","--input",help="Input MP3 file")
    parser.add_argument("-allmp3",action="store_true",help="Process all MP3 in directory")
    parser.add_argument("-d","--directory",default=".",help="Directory to scan for MP3")
    parser.add_argument("--time", help="Seconds (e.g., 20) or percentage (e.g., 10%%) to trim")
    parser.add_argument("--audioo",action="store_true",help="Use AudD API")
    parser.add_argument("--audiotag",action="store_true",help="Use AudioTag API")
    parser.add_argument("--acoustid",action="store_true",help="Use AcoustID API")
    parser.add_argument("--acr",action="store_true",help="Use ACRCloud API")
    parser.add_argument("--file","-f",help="Output results to file")
    parser.add_argument("--stat",action="store_true",help="Show summary statistics")
    parser.add_argument("--color",action="store_true",help="Color output")
    parser.add_argument("--fullinfo",action="store_true",help="Show confidence (AudioTag only)")
    parser.add_argument("--debug",choices=['full'],help="Show full debug info")
    parser.add_argument("--threads",type=int,default=1,help="Number of threads (default 1)")
    args=parser.parse_args()
    if sys.platform == "win32": os.system("")
    debug_flag = args.debug=='full'
    fullinfo_flag = args.fullinfo
    if not (args.input or args.allmp3):
        parser.print_help()
        sys.exit(1)
    services = [s for s, a in [('audioo', args.audioo), ('audiotag', args.audiotag), ('acoustid', args.acoustid), ('acr', args.acr)] if a]
    if not services:
        print("Error: you must specify at least one service: --audioo, --audiotag, --acoustid, --acr")
        sys.exit(1)
    files=[]
    if args.input: files.append(args.input)
    elif args.allmp3:
        dir_path=args.directory
        for f in os.listdir(dir_path):
            if f.lower().endswith(".mp3"): files.append(os.path.join(dir_path,f))
    print(f"{'Status'.ljust(STATUS_WIDTH)} | {'Service'.ljust(SERVICE_WIDTH)} | File")
    print("C=Copyrighted F=Free U=Unknown")
    results=[]
    for fpath in files:
        for method in services:
             res=process_file(fpath,method,args.time,args.color,debug_flag,fullinfo_flag)
             results.append(res)
    if args.file:
        with open(args.file,"w",encoding="utf-8") as fout:
            for r in results:
                fout.write(f"{r['status']} | {r['service']} | {r['file']}\n")
    if args.stat:
        total=len(results)
        c=len([r for r in results if r['status']=='C'])
        f=len([r for r in results if r['status']=='F'])
        u=len([r for r in results if r['status']=='U'])
        print(f"Total: {total}, Copyrighted: {c}, Free: {f}, Unknown: {u}")

if __name__=="__main__":
    main()