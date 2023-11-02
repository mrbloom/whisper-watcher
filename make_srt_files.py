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
mask = sys.argv[2] if len(sys.argv) > 2 else get_input("Set mask for files", "**/*.ts")
delete_files = sys.argv[3] if len(sys.argv) > 3 else get_input("Delete after transcribing files (y/Yes, n/No) ?", "n/No")
delete_files = delete_files.strip()[0].upper()
delete_files = delete_files if delete_files in ["N", "Y"] else "N"


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

def command_line(cmd):
    start_time = time.time()
    subprocess.run(cmd, shell=True)
    end_time = time.time()

    duration = end_time - start_time
    duration_td = datetime.timedelta(seconds=duration)
    dt = datetime.datetime(1, 1, 1) + duration_td

    formatted_time = dt.strftime("%H:%M:%S")
    logging.info(f"Subtitles for {file} created in {formatted_time}.")  # Log instead of print


while True:
    search_dir = os.path.join(dir_path, mask)
    for file in glob(search_dir, recursive=True):

        srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
        if not os.path.exists(srt_file) and not os.path.exists(f"{srt_file}.dummy"):

            logging.info(f"Processing: {file}")  # Log instead of print

            with open(f"{srt_file}.dummy", 'w') as dummy:
                dummy.write("PROCESSING...")

            try:
                # Checking of end of uploading file on disk
                while not is_file_ready(file):
                    pass

                cmd = f'whisper --model large-v2 "{file}" --output_dir "{dir_path}"'
                command_line(cmd)
                # waiting the appearing of subtitles
                while not os.path.exists(srt_file):
                    time.sleep(10)

                os.remove(f"{srt_file}.dummy")
                if delete_files == "Y":
                    os.remove(file)
            except:
                logging.error(f"Some problems with {file}")  # Log error instead of print
        else:
            if os.path.exists(srt_file):
                logging.warning(f"SRT file already exists for: {file}.")
            if os.path.exists(f"{srt_file}.dummy"):
                logging.warning(f"Dummy file {srt_file}.dummy already exists for: {file}. Check video file.")  # Log warning instead of print

    print("Done!")  # Log instead of print
    time.sleep(10)
