import datetime
import os
import subprocess
from glob import glob
import sys
import time


def get_input(prompt, default_value):
    """Get input from the user with a default value."""
    value = input(f"{prompt} (default: {default_value}): ")
    return value or default_value


# Check for directory argument. If not provided, use current directory.
dir_path = sys.argv[1] if len(sys.argv) > 1 else get_input("Set directory for files", ".")

# Check for mask argument. If not provided, use *.mp4.
mask = sys.argv[2] if len(sys.argv) > 2 else get_input("Set mask for files", "**/*.ts")


def get_file_size(filepath):
    # open the file in read only
    with open(filepath, "r") as file:
        # move pointer to the end of the file
        file.seek(0, 2)
        # retrieve the current position of the pointer
        # this will be the file's size in bytes
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


while True:
    # Iterate over all files based on mask in the specified directory and subdirectories
    search_dir = os.path.join(dir_path, mask)
    for file in glob(search_dir, recursive=True):  # Added recursive=True to search in subdirectories
        if is_file_ready(file):
            srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')

            if not os.path.exists(srt_file) and not os.path.exists(f"{srt_file}.dummy"):
                print(f"Processing: {file}")

                with open(f"{srt_file}.dummy", 'w') as dummy:
                    dummy.write("PROCESSING...")

                try:
                    # Start whisper in the same window
                    cmd = f'whisper --model large-v2 "{file}" --output_dir "{dir_path}"'
                    start_time = time.time()  # Capture the start time
                    subprocess.run(cmd, shell=True)
                    end_time = time.time()  # Capture the end time

                    duration = end_time - start_time
                    duration_td = datetime.timedelta(seconds=duration)
                    dt = datetime.datetime(1, 1, 1) + duration_td  # Adding to a minimum datetime value

                    formatted_time = dt.strftime("%H:%M:%S")
                    print(f"Subtitles for {file} created in {formatted_time}.")

                    # Sleep for a short duration before processing the next file
                    while not os.path.exists(srt_file):
                        time.sleep(2)

                    os.remove(f"{srt_file}.dummy")
                    os.remove(file)
                except:
                    print(f"Some problems with {file}")
            else:
                print(f"SRT file already exists for: {file} or dummy file. Check video file.")

    print("Done!")
    time.sleep(10)
