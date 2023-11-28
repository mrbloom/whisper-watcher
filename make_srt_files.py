import argparse
import datetime
import logging
import os
import subprocess
import sys
import time
from glob import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("subtitles_log.log"), logging.StreamHandler()])


def get_file_size(filepath):
    """Get the size of a file."""
    with open(filepath, "r") as file:
        file.seek(0, 2)
        return file.tell()


def is_file_ready(filepath):
    """Check if the file is ready for processing."""
    try:
        size0 = get_file_size(filepath)
        time.sleep(3)
        size1 = get_file_size(filepath)
        time.sleep(3)
        size2 = get_file_size(filepath)
        return size0 == size1 == size2
    except OSError:
        return False


def run_command_line(cmd, file, timeout):
    """Run a command line process with timeout."""
    try:
        start_time = time.time()
        subprocess.run(cmd, shell=True, timeout=timeout)
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


def transcribe_file(file, language, delete_files, add_to_timeout_sec=600):
    """Transcribe a video file."""
    srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
    if os.path.exists(srt_file) or os.path.exists(f"{srt_file}.dummy"):
        logging.warning(f"Skipping {file} as SRT or dummy file exists.")
        return

    logging.info(f"Processing: {file} with language {language}. Delete files = {delete_files}")
    open(f"{srt_file}.dummy", 'w').close()

    if not is_file_ready(file):
        logging.error(f"File {file} is not ready for processing.")
        return

    video_duration = get_video_duration(file)
    if video_duration is None:
        logging.error(f"Unable to determine video duration for {file}.")
        return

    timeout_duration = video_duration + add_to_timeout_sec
    if language.upper() == "AUTO":
        cmd = f'whisper --model large-v2 "{file}" --output_dir "{os.path.dirname(file)}"'
    else:
        cmd = f'whisper --model large-v2 "{file}" --output_dir "{os.path.dirname(file)}" --language {language}'
    run_command_line(cmd, file, timeout_duration)

    if not os.path.exists(srt_file):
        logging.error(f"SRT file {srt_file} not created for {file}.")
        return

    os.remove(f"{srt_file}.dummy")
    if delete_files == "Y":
        os.remove(file)
        logging.info(f"Deleted video file {file}.")


def transcribe_directory(directory, extensions, language, delete_files):
    """Transcribe all files in a directory with given extensions."""
    if not directory:
        logging.info("No directory specified for transcription.")
        return

    for extension in extensions:
        file_path = os.path.join(directory, f"*.{extension}")
        files = glob(file_path)
        for file in files:
            transcribe_file(file, language, delete_files)

    transcribe_language_subfolders( directory, extensions, delete_files )


def transcribe_language_subfolders(directory, extensions, delete_files):
    for extension in extensions:
        subdirs = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        supported_languages = ['English', 'Russian', 'Ukrainian']  # List of languages supported by Whisper
        audio_channel_folders = [f"{i}ch" for i in range(1,32)]

        for subdir in subdirs:
            # Check if the subdir is a supported language
            if subdir in supported_languages:
                subdir_path = os.path.join(directory, subdir)
                search_dir = os.path.join(subdir_path, f"**/*.{extension}")
                for file in glob(search_dir, recursive=True):
                    if subdir == "English":
                        transcribe_file(file, "en", delete_files)  # Use subdir name as language
                    else:
                        transcribe_file(file, subdir, delete_files)
            elif subdir in audio_channel_folders:
                pass
            else:
                logging.error(f"Directory {subdir} does not match a supported language.")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Video file transcription script.")
    parser.add_argument("-d", "--dir_path", default=".", help="Directory for files")
    parser.add_argument("-e", "--extensions", default="ts,mp4,mkv,mxf,wav,mp3", help="File extensions (comma separated)")
    parser.add_argument("-df", "--delete_files", default="N", choices=["Y", "N"],
                        help="Delete files after transcribing (Y/N)")
    parser.add_argument("-l", "--language", default="Russian", help="Language for transcribing files")

    return parser.parse_args()


def main():
    args = parse_arguments()
    args.extensions = args.extensions.split(',')

    while True:
        transcribe_directory(args.dir_path, args.extensions, args.language, args.delete_files)
        time.sleep(10)


if __name__ == "__main__":
    main()
