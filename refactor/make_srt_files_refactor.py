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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("../subtitles_log.log"), logging.StreamHandler()])

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Video file transcription script.")
    parser.add_argument("-d", "--dir_path", default=".", help="Directory for files")
    parser.add_argument("-e", "--extensions", default="ts,mp4,mkv,mxf,wav,mp3,aac",
                        help="File extensions (comma separated)")
    parser.add_argument("-df", "--delete_files", default="N", choices=["Y", "N"],
                        help="Delete files after transcribing (Y/N)")
    parser.add_argument("-l", "--language", default="Russian", help="Language for transcribing files")

    parser.add_argument("-bm", "--bk_mask", default="", help="Directory for files that works after primary directory")
    parser.add_argument("-bl", "--bk_language", default="Russian", help="Language for unprimary files")
    parser.add_argument("-bd", "--bk_delete", default="N", choices=["Y", "N"],
                        help="Delete background files after transcribing?")

    return parser.parse_args()


# def left_function(pth, extensions, language, delete):
#     if pth[-1] == '"':
#         pth = pth[:-1]  # some bug of path with spaces
#     for extension in extensions:
#         file_mask = f"*.{extension}"
#         glob_path = os.path.join(pth, file_mask)
#         for file in glob(glob_path):
#             srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
#             file_lock = f"{srt_file}.dummy"
#             if not os.path.exists(srt_file) and not os.path.exists(file_lock):
#                 transcribe_file(file, language, delete)
#                 return


def main():
    args = parse_arguments()
    args.extensions = args.extensions.split(',')

    while True:
        logging.info("Starting func transcribe_directory.")
        transcribe_directory(args.dir_path, args.extensions, args.language, args.delete_files)
        if args.bk_mask:
            logging.info("Starting func left_function.")
            left_function(args.bk_mask, args.extensions, args.bk_language, args.bk_delete)
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        # Log the exception with the formatted traceback
        logging.error("Exception occurred: %s", tb)
