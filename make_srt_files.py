import datetime
import os
import subprocess
from glob import glob
import sys
import time
import logging  # Import the logging module

# 1. Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("subtitles_log.log"),
                              logging.StreamHandler()])


def get_input(prompt, default_value):
    """Get input from the user with a default value."""
    value = input(f"{prompt} (default: {default_value}): ")
    return value or default_value


dir_path = sys.argv[1] if len(sys.argv) > 1 else get_input("Set directory for files", ".")
extensions = sys.argv[2] if len(sys.argv) > 2 else get_input("Set file extensions (comma separated)", "ts,mp4,mkv,mxf")
# Split the extensions string into a list of individual extensions
extensions = extensions.split(',')

# mask = sys.argv[2] if len(sys.argv) > 2 else get_input("Set mask for files", "**/*.ts")
delete_files = sys.argv[3] if len(sys.argv) > 3 else get_input("Delete after transcribing files (Y/Yes, N/No) ?",
                                                               "n/No")
delete_files = delete_files.strip()[0].upper()
delete_files = delete_files if delete_files in ["N", "Y"] else "N"

language = sys.argv[4] if len(sys.argv) > 4 else get_input(
    "Set language for transcribing files (default: Russian) for auto detect enter 'auto' ?", "Russian")
if language.strip().upper()[:4] == "AUTO":
    language = "AUTO"
else:
    language = language.title()

primary_folder = sys.argv[5] if len(sys.argv) > 5 else get_input(
    "Set primary folder to watch after every transcribing (default: No primary folder '')", "")

delete_primary_files = sys.argv[6] if len(sys.argv) > 6 else get_input(
    "Delete videos in primary folder after the transcribing (default: Y/Yes, N/No", "N")

primary_language = sys.argv[7] if len(sys.argv) > 7 else get_input(
    f"Set language for transcribing files in primary folder (default: auto for autodetect)","auto")

def get_file_size(filepath):
    with open(filepath, "r") as file:
        file.seek(0, 2)
        size = file.tell()
        return size


def is_file_ready(filepath):
    try:
        size0 = get_file_size(filepath)
        time.sleep(3)
        size1 = get_file_size(filepath)
        time.sleep(3)
        size2 = get_file_size(filepath)
        return size0 == size1 == size2
    except OSError:
        return False


def command_line(cmd, file, timeout):
    try:
        start_time = time.time()
        subprocess.run(cmd, shell=True, timeout=timeout)
        end_time = time.time()

        duration = end_time - start_time
        duration_td = datetime.timedelta(seconds=duration)
        dt = datetime.datetime(1, 1, 1) + duration_td

        formatted_time = dt.strftime("%H:%M:%S")
        logging.info(f"Subtitles for {file} created in {formatted_time}.")
    except subprocess.TimeoutExpired:
        logging.error(f"Process for {file} timed out. Terminating the process and moving to next file.")


def get_video_duration(file):
    """Get the duration of the video file in seconds."""
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file}\""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        duration = float(result.stdout)
        return duration
    except Exception as e:
        logging.error(f"Error getting duration for {file}: {e}")
        return None


def transcribe_file(file, language, delete_files, add_to_timeout_sek=600):
    try:
        srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
        if not os.path.exists(srt_file) and not os.path.exists(f"{srt_file}.dummy"):

            logging.info(f"Processing: {file}")  # Log instead of print

            with open(f"{srt_file}.dummy", 'w') as dummy:
                dummy.write("PROCESSING...")

            try:
                # Checking of end of uploading file on disk
                while not is_file_ready(file):
                    pass

                # Get video duration
                video_duration = get_video_duration(file)
                if video_duration is None:
                    raise Exception("Unable to determine video duration")

                # Set a longer timeout than the duration of the video
                timeout_duration = video_duration + add_to_timeout_sek  # Adding 10 minutes buffer
                logging.info(f"Set timeout for processing: {file} equal to {timeout_duration}")  # Log instead of print

                if language.upper() == "AUTO":
                    cmd = f'whisper --model large-v2 "{file}" --output_dir "{os.path.dirname(file)}"'
                else:
                    cmd = f'whisper --model large-v2 "{file}" --output_dir "{os.path.dirname(file)}" --language {language}'
                command_line(cmd, file, timeout_duration)
                # waiting the appearing of subtitles
                while not os.path.exists(srt_file):
                    time.sleep(10)

                os.remove(f"{srt_file}.dummy")
                if delete_files == "Y":
                    print(f"Deleting video file {file}")
                    os.remove(file)
            except:
                logging.error(f"Some problems with {file}")  # Log error instead of print
        else:
            if os.path.exists(srt_file):
                logging.warning(f"SRT file already exists for: {file}.")
            if os.path.exists(f"{srt_file}.dummy"):
                logging.warning(
                    f"Dummy file {srt_file}.dummy already exists for: {file}. Check video file.")  # Log warning instead of print
    except Exception as e:
        logging.error(f"Some problems with {file}: {e}")


def transcribe_folder(dir_path,extension,language, delete_files, alias):
    if dir_path!="":
        search_dir = os.path.join(dir_path, f"**/*.{extension}")
        for file in glob(search_dir, recursive=True):
            transcribe_file(file, language, delete_files)
    else:
        print(f"Directory for folder {alias} **/*.{extension} is empty.")

while True:
    for extension in extensions:  # Loop over each extension
        # look for files in primary folder
        transcribe_folder(primary_folder,extension,primary_language,delete_primary_files,"primary")

    for extension in extensions:  # Loop over each extension
        #look file in secondary folder`
        search_dir = os.path.join(dir_path, f"**/*.{extension}")
        for file in glob(search_dir, recursive=True):
            transcribe_file(file, language, delete_files)
            #after transcribing look for files in primary folder
            for extension in extensions:
                transcribe_folder(primary_folder,extension,primary_language,delete_primary_files, "primary")

    # print("Done!")  # Log instead of print
    time.sleep(10)
