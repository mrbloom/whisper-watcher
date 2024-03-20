import argparse
import datetime
import logging
import os
import subprocess
import threading
import time
from glob import glob
import traceback
from random import random
from reduplicate import make_reduplicate


def initialize_logging(log_file_path):
    """
    Initializes logging with the specified log file path. Ensures that the directory for the log file exists.

    Args:
    log_file_path: str. The path where the log file should be stored.
    """
    # Extract the directory path from the log file path
    log_directory = os.path.dirname(log_file_path)

    # Create the directory if it does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)

    # Configure logging to use the log file path
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file_path), logging.StreamHandler()])


def get_file_size(filepath):
    """Get the size of a file."""
    with open(filepath, "r") as file:
        file.seek(0, 2)
        return file.tell()


def is_file_ready(filepath, timeout=12):
    try:
        """Check if the file is ready for processing."""
        size0 = get_file_size(filepath)
        time.sleep(timeout)
        size1 = get_file_size(filepath)
        if size1 != size0:
            return False
        return True
    except OSError:
        return False


def run_command_line(cmd, file, timeout):
    """Run a command line process with timeout."""
    try:
        start_time = time.time()
        """Run a command line process with timeout and deduplicate SRT file afterwards."""
        try:
            subprocess.run(cmd, shell=True, timeout=timeout)
            # Assuming SRT file is named as the video file but with .srt extension
            srt_file_path = os.path.splitext(file)[0] + '.srt'
            if os.path.exists(srt_file_path):
                make_reduplicate(srt_file_path)
            logging.info(f"Subtitles for {file} created and deduplicated.")
        except subprocess.TimeoutExpired:
            logging.error(f"Process for {file} timed out. Terminating the process and moving to next file.")
        except Exception as e:
            logging.error(f"An error occurred while processing {file}: {e}")
        end_time = time.time()

        duration = datetime.timedelta(seconds=end_time - start_time)
        formatted_time = (datetime.datetime(1, 1, 1) + duration).strftime("%H:%M:%S")
        logging.info(f"Subtitles for {file} created in {formatted_time}.")
    except subprocess.TimeoutExpired:
        logging.error(f"Process for {file} timed out. Terminating the process and moving to next file.")


def get_video_duration(file):
    """Get the duration of the video file in seconds."""
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file}\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return float(result.stdout)
    except Exception as e:
        logging.error(f"Error getting duration for {file}: {e}")
        return None


def transcribe_file(file, language, delete_files, task, model, add_to_timeout_sec=600):
    """Transcribe a video file."""
    srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
    if os.path.exists(srt_file):
        logging.warning(f"Skipping {file} as SRT exists.")
        return

    if not is_file_ready(file):
        logging.error(f"File {file} is not ready for processing.")
        return

    time.sleep(random() * 1)  #### Why? What the fuck
    if os.path.exists(f"{srt_file}.dummy"):
        logging.warning(f"Skipping {file} as dummy file exists.")
        return
    else:
        open(f"{srt_file}.dummy", 'w').close()

    video_duration = get_video_duration(file)
    if video_duration is None:
        logging.error(f"Unable to determine video duration for {file}.")
        return

    logging.info(
        f"Processing: {file} with language {language}. Delete files = {delete_files}. Duration = {video_duration / 60} min.")

    timeout_duration = video_duration + add_to_timeout_sec
    if language.upper() == "AUTO":
        cmd = f'whisper --model {model} "{file}" --output_dir "{os.path.dirname(file)}" --device cuda --output_format srt --task {task}'
    else:
        cmd = f'whisper --model {model} "{file}" --output_dir "{os.path.dirname(file)}" --language {language} --device cuda --output_format srt --task {task}'
    run_command_line(cmd, file, timeout_duration)

    if not os.path.exists(srt_file):
        logging.error(f"SRT file {srt_file} not created for {file}.")
        return

    os.remove(f"{srt_file}.dummy")
    if delete_files == "Y":
        os.remove(file)
        logging.info(f"Deleted video file {file}.")


def transcribe_directory(directory, extensions, language, delete_files, task, model):
    """Transcribe all files in a directory with given extensions."""
    if not directory:
        logging.info(f"No directory {directory} specified for transcription.")
        return

    logging.info(f"Transcribing files in {directory}.")
    for extension in extensions:
        file_path = os.path.join(directory, f"**\\*.{extension}")
        files = glob(file_path, recursive=True)
        # print(f"files = {files}")
        logging.info(f"Looking for files with {extension} in {file_path}")
        for file in files:
            transcribe_file(file, language, delete_files, task, model)
            logging.info(f"Move to next file from func transcribe_directory. File was {file}")

    # transcribe_language_subfolders(directory, extensions, delete_files, task)


# def transcribe_language_subfolders(directory, extensions, delete_files, task):
#     for extension in extensions:
#         subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
#         supported_languages = ['English', 'Russian', 'Ukrainian']  # List of languages supported by Whisper
#         audio_channel_folders = [f"{i}ch" for i in range(1, 32)]
#
#         for subdir in subdirs:
#             # Check if the subdir is a supported language
#             if subdir in supported_languages:
#                 subdir_path = os.path.join(directory, subdir)
#                 search_dir = os.path.join(subdir_path, f"**/*.{extension}")
#                 for file in glob(search_dir, recursive=True):
#                     if subdir == "English":
#                         transcribe_file(file, "en", delete_files, task)  # Use subdir name as language
#                     else:
#                         transcribe_file(file, subdir, delete_files, task)
#                     logging.info(f"Move to next file from func transcribe_lanuage_subfolders. File was {file}")
#             elif subdir in audio_channel_folders:
#                 pass
#             elif subdir == 'multilang':
#                 pass
#             elif subdir == '!bugs':
#                 pass
#             else:
#                 logging.error(f"Directory {subdir} does not match a supported language.")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Video file transcription script.")
    parser.add_argument("-d", "--dir_path", default=".", help="Directory for files")
    parser.add_argument("-e", "--extensions", default="ts,mp4,mkv,mxf,wav,mp3,aac",
                        help="File extensions (comma separated)")
    parser.add_argument("-df", "--delete_files", default="N", choices=["Y", "N"],
                        help="Delete files after transcribing (Y/N)")
    parser.add_argument("-l", "--language", default="Russian", help="Language for transcribing files")
    parser.add_argument("-t", "--task", default="transcribe", help="Task for whisper files")
    parser.add_argument("-m", "--model", default="large-v3", help="Model of whisper")

    parser.add_argument("-bm", "--bk_mask", default="", help="Directory for files that works after primary directory")
    parser.add_argument("-bl", "--bk_language", default="Russian", help="Language for unprimary files")
    parser.add_argument("-bd", "--bk_delete", default="N", choices=["Y", "N"],
                        help="Delete background files after transcribing?")
    parser.add_argument("-bt", "--bk_task", default="transcribe", help="Task for not primary folder whisper files")

    return parser.parse_args()


def left_function(pth, extensions, language, delete, task, model):
    if pth[-1] == '"':
        pth = pth[:-1]  # some bug of path with spaces
    for extension in extensions:
        file_mask = f"*.{extension}"
        glob_path = os.path.join(pth, file_mask)
        for file in glob(glob_path):
            srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
            file_lock = f"{srt_file}.dummy"
            if not os.path.exists(srt_file) and not os.path.exists(file_lock):
                transcribe_file(file, language, delete, task, model)
                return


def main():
    log_file_path = r"Z:\fast_channels\OTERRA\!LOGS\whisper_logs.txt"
    initialize_logging(log_file_path)

    args = parse_arguments()
    args.extensions = args.extensions.split(',')

    while True:
        logging.info(f"Starting func transcribe_directory for {args.dir_path}.")
        transcribe_directory(args.dir_path, args.extensions, args.language, args.delete_files, args.task, args.model)
        if args.bk_mask:
            logging.info("Starting func left_function.")
            left_function(args.bk_mask, args.extensions, args.bk_language, args.bk_delete, args.bk_task, args.model)
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        # Log the exception with the formatted traceback
        logging.error("Exception occurred: %s", tb)
