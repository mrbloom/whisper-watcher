import subprocess
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os


class Watcher:

    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer stopped")
        self.observer.join()


max_whispers = 1
whisper_thread_number = 0


class Handler(FileSystemEventHandler):
    @staticmethod
    def get_file_size(filepath):
        # open the file in read only
        with open(filepath, "r") as file:
            # move pointer to the end of the file
            file.seek(0, 2)
            # retrieve the current position of the pointer
            # this will be the file's size in bytes
            size = file.tell()
            return size

    def is_file_ready(self, filepath):
        try:
            size0 = self.get_file_size(filepath)
            time.sleep(3)
            size1 = self.get_file_size(filepath)
            time.sleep(3)
            size2 = self.get_file_size(filepath)
            return size0 == size1 == size2
        except OSError:
            return False

    def on_created(self, event):
        global whisper_thread_number
        global max_whispers
        while max_whispers <= whisper_thread_number:
            time.sleep(10)
        if not event.is_directory and event.event_type == 'created':
            if event.src_path.endswith(('.mp4', '.mkv', '.avi', '.mov', '.ts')):  # Check for video file extensions
                print(f"Created file {event.src_path}")
                whisper_thread_number += 1
                # Wait for the file to be completely uploaded or copied
                while not self.is_file_ready(event.src_path):
                    time.sleep(2)  # Adjust the sleep duration as needed
                # Now process the file
                generate_subtitles(event.src_path)
                whisper_thread_number -= 1


def generate_subtitles(video_path):
    # The command you want to run in a separate window
    cmd = f"whisper --model large-v2 {video_path}"
    if whisper_thread_number<max_whispers:
        # Open a new command prompt window and run the command
        subprocess.run(["start", "cmd", "/K", cmd], shell=True)
    else:
        subprocess.call(["start", "cmd", "/K", cmd], shell=True)
    # Optionally, remove the temporary audio file after processing
    # os.remove(audio_path)


if __name__ == '__main__':
    watchdog_folder = input("Enter watchdog folder : ")
    watcher = Watcher(watchdog_folder)
    watcher.run()
