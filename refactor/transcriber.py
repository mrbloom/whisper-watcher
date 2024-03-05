import argparse
import datetime
import logging
import os
import subprocess

import time
from glob import glob

from random import random



class FileTranscriber:
    def __init__(self, language='AUTO', delete_files=False):
        self.language = language
        self.delete_files = delete_files

    @staticmethod
    def get_file_size(filepath):
        with open(filepath, "r") as file:
            file.seek(0, 2)
            return file.tell()

    @staticmethod
    def is_file_ready(filepath, timeout=12):
        try:
            size0 = FileTranscriber.get_file_size(filepath)
            time.sleep(timeout)
            size1 = FileTranscriber.get_file_size(filepath)
            return size1 == size0
        except OSError:
            return False

    @staticmethod
    def get_video_duration(file):
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 \"{file}\""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return float(result.stdout)
        except Exception as e:
            logging.error(f"Error getting duration for {file}: {e}")
            return None

    def transcribe(self, file):
        if not self.is_file_ready(file):
            logging.error(f"File {file} is not ready for processing.")
            return False

        srt_file = os.path.join(os.path.splitext(file)[0] + '.srt')
        if os.path.exists(srt_file) or os.path.exists(f"{srt_file}.dummy"):
            logging.warning(f"Skipping {file} as SRT exists or dummy file present.")
            return False

        open(f"{srt_file}.dummy", 'w').close()
        video_duration = self.get_video_duration(file)
        if video_duration is None:
            os.remove(f"{srt_file}.dummy")
            return False

        cmd = self.construct_command(file, video_duration)
        if cmd:
            self.run_command_line(cmd, file, video_duration + 600)  # Add additional timeout buffer

            if not os.path.exists(srt_file):
                logging.error(f"SRT file {srt_file} not created for {file}.")
                os.remove(f"{srt_file}.dummy")
                return False

            if self.delete_files:
                os.remove(file)
                logging.info(f"Deleted video file {file}.")

            return True
        return False

    def construct_command(self, file, video_duration):
        base_cmd = f'whisper --model large-v3 "{file}" --output_dir "{os.path.dirname(file)}" --output_format srt'
        if self.language.upper() != "AUTO":
            base_cmd += f' --language {self.language}'
        return base_cmd + ' --device cuda'

    @staticmethod
    def run_command_line(cmd, file, timeout):
        try:
            subprocess.run(cmd, shell=True, timeout=timeout)
            logging.info(f"Process for {file} completed successfully.")
        except subprocess.TimeoutExpired:
            logging.error(f"Process for {file} timed out. Terminating the process.")


class FolderTranscriber:
    def __init__(self, directory, extensions, language='AUTO', delete_files=False):
        self.directory = directory
        self.extensions = extensions.split(',')
        self.language = language
        self.delete_files = delete_files
        self.file_transcriber = FileTranscriber(language, delete_files)

    def transcribe_folders(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if any(file.endswith(ext) for ext in self.extensions):
                    full_path = os.path.join(root, file)
                    self.file_transcriber.transcribe(full_path)


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