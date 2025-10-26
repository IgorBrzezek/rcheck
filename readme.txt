=================================================
 rcheck - Copyright Checker for Audio Files
=================================================

0. Version
-------------
This is for version 0.1alpha 
Date: 25.10.2025

1. Purpose and Goal
-----------------------
`rcheck` is an advanced Python script designed to check whether an audio track is protected by copyright. It is particularly useful for content creators (e.g., on YouTube) who want to avoid copyright claims and the blocking of their videos.

The script identifies music tracks by using several leading audio recognition services and reports whether a given track was found in their databases.

2. Required Dependencies and Installation
------------------------------------
For the script to function correctly, you must install several external tools and Python libraries.

### Step 1: Install FFmpeg
FFmpeg is essential for audio processing (reading duration, trimming).
- **Windows**: Download from the [official FFmpeg website](https://ffmpeg.org/download.html) and add the `bin` folder to your system's `PATH` environment variable.
- **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install ffmpeg`
- **macOS (Homebrew)**: `brew install ffmpeg`

### Step 2: Install Python Libraries
Open your terminal or command prompt and install all required libraries with the following command:

```
pip install colorama requests requests-toolbelt pyacoustid acrcloud-sdk-python
```

### Step 3: Configure API Keys
Open the `rcheck.py` file in a text editor and fill in your API keys for the services you intend to use. They are located at the beginning of the file.

- `ACOUSTID_API_KEY`: Key for the AcoustID service.
- `AUDIOTAG_API_KEY`: Key for the audiotag.info service.
- `AUDD_API_KEY`: Key for the audd.io service.
- `ACRCLOUD_CONFIG`: Fill in the `host`, `access_key`, and `access_secret` for the ACRCloud service.

3. Available Options (Command-Line Arguments)
---------------------------------------------
The script can be configured using the following arguments:

- `-i`, `--input`: Path to a single MP3 file or a directory to scan.
- `-allmp3`: Process all `.mp3` files in the specified directory.
- `-d`, `--directory`: Specifies the directory to scan (default is the current directory).
- `--time`: Trim the audio for analysis. You can provide seconds (e.g., `20`) or a percentage (e.g., `15%`).
- `--audioo`: Use the AudD service for recognition.
- `--audiotag`: Use the AudioTag service for recognition.
- `--acoustid`: Use the AcoustID service for recognition.
- `--acr`: Use the ACRCloud service for recognition.
- `--file`, `-f`: Save the results to the specified text file.
- `--stat`: Display summary statistics after the process is complete.
- `--color`: Enable colored output in the terminal.
- `--fullinfo`: Display additional information, such as match confidence (only works with `--audiotag`).
- `--debug full`: Enable debug mode, which shows the full communication with the API.
- `--threads`: Number of threads for concurrent file processing (default is 1).

4. Usage Examples
--------------------

**Example 1: Check a single file using ACRCloud**
Checks one file and displays the result in color.
```
python rcheck.py -i "path/to/your/file.mp3" --acr --color
```

**Example 2: Check all MP3 files in the current directory using AcoustID**
Scans all `.mp3` files and displays a summary at the end.
```
python rcheck.py -allmp3 --acoustid --stat
```

**Example 3: Check the first 30 seconds of a file using AudD**
Analyzes only the initial 30 seconds of the track, which speeds up the process.
```
python rcheck.py -i "another/file.mp3" --audioo --time 20
```

**Example 4: Check 10% of a track's length using AudioTag with full info**
Analyzes the initial 10% of the track and displays additional information about the match.
```
python rcheck.py -i "file.mp3" --audiotag --time 10% --fullinfo
```

**Example 5: Check all files in a given directory using all services and save the results to a file**
Uses all four services to check each file and saves the logs to `results.txt`.
```
python rcheck.py -allmp3 -d "path/to/your/folder" --audioo --audiotag --acoustid --acr --file results.txt
```

**Example 6: Check a file with debug mode enabled**
Useful for diagnosing problems, as it shows the full communication with the service's API.
```
python rcheck.py -i "file.mp3" --acr --debug full