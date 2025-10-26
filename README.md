# rcheck - Copyright Checker for Audio Files

[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An advanced Python script designed to check whether audio tracks are protected by copyright. Perfect for content creators who want to avoid copyright claims and video blocks on platforms like YouTube.

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command-Line Options](#command-line-options)
- [Examples](#examples)
- [Supported Services](#supported-services)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Features

- **Multi-Service Recognition**: Supports four leading audio recognition services
- **Flexible Input**: Process single files or entire directories
- **Audio Trimming**: Analyze only portions of tracks for faster processing
- **Real-Time Progress**: Visual progress bars for uploads and processing
- **Concurrent Processing**: Multi-threaded processing for batch operations
- **Colored Output**: Enhanced terminal output with color coding
- **Detailed Logging**: Debug mode for troubleshooting API issues
- **Export Results**: Save results to files for later analysis
- **Statistics**: Summary reports of copyright status across files

## How It Works

The script identifies music tracks by sending audio samples to various recognition services. Each service maintains a database of known tracks and returns metadata if a match is found. The script then reports whether the track is likely copyrighted based on the service's response.

### Status Codes
- **C (Copyrighted)**: Track found in service database
- **F (Free)**: Track not found on major platforms (AudD only)
- **U (Unknown)**: Track not found or service error

## Installation

### Prerequisites

#### FFmpeg
FFmpeg is required for audio processing (duration reading, trimming).

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

#### Python Libraries
Install all required Python packages:
```bash
pip install colorama requests requests-toolbelt pyacoustid acrcloud-sdk-python
```

## Configuration

### API Keys Setup

1. Open `rcheck.py` in a text editor
2. Locate the API configuration section at the top
3. Fill in your API keys for desired services:

```python
# AcoustID API Key
ACOUSTID_API_KEY = "your_acoustid_key_here"

# AudioTag API Key
AUDIOTAG_API_KEY = "your_audiotag_key_here"

# AudD API Key
AUDD_API_KEY = "your_audd_key_here"

# ACRCloud Configuration
ACRCLOUD_CONFIG = {
    'host': 'identify-eu-west-1.acrcloud.com',  # Your region
    'access_key': 'your_access_key_here',
    'access_secret': 'your_access_secret_here',
    'debug': False,
    'timeout': 10
}
```

### Obtaining API Keys

- **AcoustID**: Free registration at [acoustid.org](https://acoustid.org/)
- **AudioTag**: Get key from [audiotag.info](https://audiotag.info/)
- **AudD**: Register at [audd.io](https://audd.io/)
- **ACRCloud**: Sign up at [acrcloud.com](https://acrcloud.com/)

## Usage

### Basic Syntax
```bash
python rcheck.py [options] [service_flags]
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `-i, --input PATH` | Path to single MP3 file or directory |
| `-allmp3` | Process all MP3 files in directory |
| `-d, --directory DIR` | Directory to scan (default: current) |
| `--time VALUE` | Trim audio: seconds (e.g., `20`) or percentage (e.g., `15%`) |
| `--audioo` | Use AudD service |
| `--audiotag` | Use AudioTag service |
| `--acoustid` | Use AcoustID service |
| `--acr` | Use ACRCloud service |
| `-f, --file PATH` | Save results to file |
| `--stat` | Show summary statistics |
| `--color` | Enable colored output |
| `--fullinfo` | Show confidence scores (AudioTag only) |
| `--debug full` | Enable debug mode |
| `--threads N` | Number of processing threads (default: 1) |

## Examples

### Example 1: Single File Check
Check one file using ACRCloud with colored output:
```bash
python rcheck.py -i "music/track.mp3" --acr --color
```

### Example 2: Directory Scan
Scan all MP3 files in current directory using AcoustID:
```bash
python rcheck.py -allmp3 --acoustid --stat
```

### Example 3: Fast Analysis
Analyze only first 30 seconds using AudD:
```bash
python rcheck.py -i "long_track.mp3" --audioo --time 30
```

### Example 4: Detailed Results
Check 10% of track with full AudioTag information:
```bash
python rcheck.py -i "track.mp3" --audiotag --time 10% --fullinfo
```

### Example 5: Multi-Service Batch
Check all files in directory using all services:
```bash
python rcheck.py -allmp3 -d "music/" --audioo --audiotag --acoustid --acr --file results.txt
```

### Example 6: Debug Mode
Troubleshoot API issues with full logging:
```bash
python rcheck.py -i "problematic.mp3" --acr --debug full
```

## Supported Services

### AcoustID
- **Method**: Local fingerprinting, remote lookup
- **Pros**: Fast, no upload required, high accuracy
- **Cons**: Limited metadata, requires local processing

### AudioTag
- **Method**: File upload with async processing
- **Pros**: Detailed metadata, confidence scores
- **Cons**: Slower due to async processing

### AudD
- **Method**: File upload with platform checking
- **Pros**: Checks multiple streaming platforms
- **Cons**: API limits, potential false negatives

### ACRCloud
- **Method**: Advanced fingerprinting via SDK
- **Pros**: High accuracy, commercial-grade
- **Cons**: Requires SDK installation

## Troubleshooting

### Common Issues

**"FFmpeg not found"**
- Ensure FFmpeg is installed and in your PATH
- Restart your terminal/command prompt

**"API limit reached"**
- Check your API usage on the service's dashboard
- Consider upgrading your plan or waiting for reset

**"Audio is too short" (AudioTag)**
- Use `--time` with a larger value or remove it entirely
- AudioTag requires minimum length for reliable matching

**No colored output on Windows**
- The script automatically enables ANSI colors on Windows CMD
- If colors don't appear, try using Windows Terminal or PowerShell

### Debug Mode
Use `--debug full` to see detailed API communication:
```bash
python rcheck.py -i "file.mp3" --acr --debug full
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Version History

- **v0.1** (2025-10-25): Initial release with multi-service support
  - Added ACRCloud integration
  - Improved performance with FFmpeg
  - Enhanced error handling and logging

---

For questions or support, please check the troubleshooting section or create an issue on GitHub.