# BatchYoutubeDownloader

[![forthebadge](https://forthebadge.com/images/badges/60-percent-of-the-time-works-every-time.svg)](https://forthebadge.com) ![GitHub top language](https://img.shields.io/github/languages/top/c0derMo/batchyoutubedownloader?style=for-the-badge)

A tool for downloading a list of YouTube videos, and cutting them to size with a set starting point & duration for each video.

This tool uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ffmpy](https://github.com/Ch00k/ffmpy).
ffmpy relies on FFmpeg, so make sure you have that installed and accessible in your path variable.

# Usage
1. Clone / download the repository
2. Install the requirements using `pip install -r requirements.txt`
3. Access the commandline interface using `python batchDownloader.py [LIST]`

Supply the path to a list file in `[LIST]`.
The list file should contain all your videos, with starting times & durations, formated as such:

`[VIDEO URL] | [STARTING TIME] | [DURATION]`

with times formatted as: `HH:MM:SS`.

The tool will then do the following:
1. Use yt-dlp to download the video to `./raw_downloads/`
2. Use ffmpeg to remux & cut down the video, save that to `./output/`

The files in `./output/` will be enumerated using the line numbers of the list file.

## Commandline arguments:
- `-h`: Displays information about the commandline arguments.
- `-b` / `--begin_offset`: Offset the starting time of each video by subtracting the supplied amount of seconds off the starting time.
- `-d` / `--duration_offset`: Offset the duration of each video by adding the supplied amount of seconds to the duration.
- `-o` / `--override`: Override already existing files in `./output/`.
- `-i` / `--ignore_errors`: Ignore the errors in the supplied list file. The lines with errors will be ignored.
- `-c` / `--clean`: Clean the `./raw_downloads/`-folder upon finishing, to free up a bunch of disk space since all the full-length video files are stored there before getting cut to size.