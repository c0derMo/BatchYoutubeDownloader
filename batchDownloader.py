from ffmpy import FFmpeg, FFRuntimeError
from yt_dlp import YoutubeDL
from yt_dlp.postprocessor import PostProcessor
from pathlib import Path
import argparse
import sys
import re
import os
import glob


class TrimPostProcessor(PostProcessor):
    def __init__(self, starting_time, duration, final_filename, arguments):
        super().__init__(self)
        self.starting_time = subtract_from_time(starting_time, seconds=arguments.begin_offset)
        self.duration = add_to_time(duration, seconds=arguments.duration_offset)
        self.final_filename = final_filename
        self.arguments = arguments
    def run(self, info):
        print("Cutting video " + info.get("filepath") + " from " + self.starting_time + " with length " + self.duration + "...")
        global_options = ""
        if self.arguments.override:
            global_options += "-y "
        else:
            global_options += "-n "
        if not self.arguments.verbose:
            global_options += '-hide_banner -loglevel error'
        try:
            FFmpeg(
                global_options=global_options,
                inputs={info.get("filepath"): None},
                outputs={'./output/' + self.final_filename: '-ss ' + self.starting_time + ' -t ' + self.duration}
            ).run()
        except FFRuntimeError:
            print("Error when cutting video " + info.get("filepath") + "!")
        return [], info


def download_video(video, final_filename, args):
    print("Downloading video of " + video[0] + "...")
    ydl_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': './raw_downloads/%(id)s',
        'keepvideo': args.keep_original,
        'quiet': not args.verbose
    }
    ydl = YoutubeDL(ydl_opts)
    ydl.add_post_processor(TrimPostProcessor(video[1], video[2], final_filename, args))
    ydl.download([video[0]])


def add_to_time(time, hours=0, minutes=0, seconds=0):
    """
    Add time to a time-string of the format HH:MM:SS
    """
    split_time = time.split(":")
    in_seconds = int(split_time[0]) * 3600 + int(split_time[1]) * 60 + int(split_time[2])
    in_seconds += hours * 3600 + minutes * 60 + seconds

    new_hours = in_seconds // 3600
    in_seconds %= 3600
    new_minutes = in_seconds // 60
    in_seconds %= 60
    return "%02i:%02i:%02i" % (new_hours, new_minutes, in_seconds)


def subtract_from_time(time, hours=0, minutes=0, seconds=0):
    """
    Subtract time from a time-string of the format HH:MM:SS
    """
    split_time = time.split(":")
    in_seconds = int(split_time[0]) * 3600 + int(split_time[1]) * 60 + int(split_time[2])
    in_seconds -= hours * 3600 + minutes * 60 + seconds
    if in_seconds < 0:
        return "00:00:00"

    new_hours = in_seconds // 3600
    in_seconds %= 3600
    new_minutes = in_seconds // 60
    in_seconds %= 60
    return "%02i:%02i:%02i" % (new_hours, new_minutes, in_seconds)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download a list of YouTube videos and cut them to a set size.')
    parser.add_argument('list', type=str, help="Path to a list file containing video-links, starting timestamps and durations in the format '[LINK] | [STARTING TIME] | [DURATION]' with times supplied in HH:MM:SS.")
    parser.add_argument('-b', '--begin_offset', type=int, help="Offsets the starting time of the videos by subtracting the supplied amount of seconds.", default=0)
    parser.add_argument('-d', '--duration_offset', type=int, help="Offsets the duration of the videos by adding the supplied amount of seconds.", default=0)
    parser.add_argument('-o', '--override', action='store_true', help="Override existing files in output folder.")
    parser.add_argument('-i', '--ignore_errors', action='store_true', help="Ignore errors in the supplied list. Invalid lines will be fully ignored.")
    parser.add_argument('-c', '--clean', action='store_true', help="Clean the raw_downloads directory after finishing, removing all the non-cut videos to free up disk space.")
    parser.add_argument('-k', '--keep-original', action='store_true', help='Instruct yt-dlp to keep the unmerged files. Takes up additional disk space.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging for yt-dlp and ffmpeg.')
    args = parser.parse_args()

    Path("./raw_downloads").mkdir(exist_ok=True)
    Path("./output").mkdir(exist_ok=True)

    try:
        with open(args.list, 'r') as f:
            video_list = f.read().split("\n")
            f.close()
    except FileNotFoundError:
        print("List " + args.list + " not found! Exiting.")
        sys.exit(1)
    
    parsed_video_list = []
    for (line_number, video_line) in enumerate(video_list, 1):
        splitted_line = video_line.split(" | ")
        if len(splitted_line) != 3:
            print("Line " + str(line_number) + " isn't formatted correctly! Expected colums: 3. Found: " + str(len(splitted_line)))
            if not args.ignore_errors:
                sys.exit(1)
            else:
                continue
        if not re.match("\d+:\d+:\d+", splitted_line[1]) or not re.match("\d+:\d+:\d+", splitted_line[2]):
            print("Line " + str(line_number) + " isn't formatted correctly! Times aren't formatted as HH:MM:SS.")
            if not args.ignore_errors:
                sys.exit(1)
            else:
                continue
        parsed_video_list.append((splitted_line[0], subtract_from_time(splitted_line[1], seconds=args.begin_offset), add_to_time(splitted_line[2], seconds=args.duration_offset)))
    
    print("Parsed " + args.list + " with " + str(len(parsed_video_list)) + " videos.")
    for (idx, video) in enumerate(parsed_video_list, 1):
        print("==[ Video #" + str(idx) + " ]==")
        download_video(video, str(idx) + ".mp4", args)
    print("Finished downloading videos!")
    if args.clean:
        print("Cleaning ./raw_downloads folder...")
        for files in glob.glob("./raw_downloads/*"):
            os.remove(files)
        print("Done!")