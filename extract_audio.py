import argparse
import re
import subprocess
import os
import glob
import time


# Function to extract a specific audio channel
def extract_audio(input_video_path, output_audio_path, channel):
    try:
        command = [
            'ffmpeg',
            '-i', input_video_path,  # Input file
            '-map', f'0:a:{channel - 1}',  # Selecting the specific audio stream
            '-c:a', 'copy',  # Copying the audio codec (no encoding)
            output_audio_path  # Output file
        ]
        subprocess.run(command, check=True)
        print(f"Audio channel {channel} extracted to '{output_audio_path}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Determine the correct file extension based on the codec
def get_audio_extension(codec_name):
    if codec_name == "mp3":
        return "mp3"
    elif codec_name == "aac":
        return "aac"
    elif codec_name == "vorbis":
        return "ogg"
    elif codec_name == "opus":
        return "opus"
    # Add more mappings as needed
    else:
        return "audio"  # Generic extension for unknown codecs

# Function to get codec of the first audio stream using ffprobe
def get_audio_codec(file_path):
    try:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        codec = result.stdout.strip()
        return codec
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while getting audio codec: {e}")
        return None

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

# Watching folders and processing files
# Watching folders and processing files with root directory
def watch_and_process(root_folder, folders, extensions):
    for folder in folders:
        full_folder_path = os.path.join(root_folder, folder)
        if not os.path.exists(full_folder_path):
            print(f"Folder does not exist: {full_folder_path}")
            continue

        channel = int(folder.replace('ch', ''))

        for ext in extensions:
            for video_file in glob.glob(f"{full_folder_path}/*.{ext}"):
                codec = get_audio_codec(video_file)
                if codec:
                    print(f'Processing {video_file}...')
                    extension = get_audio_extension(codec)
                    audio_file = f"{video_file.rsplit('.', 1)[0]}_{channel}_channel.{extension}"
                    if is_file_ready(video_file):
                        extract_audio(video_file, audio_file, channel)
                        os.remove(video_file)
                        print(f"Deleted video file: {video_file}")
                else:
                    print(f"Could not determine codec for {video_file}")

# Function to extract a specific audio channel
def extract_audio(input_video_path, output_audio_path, channel):
    try:
        command = [
            'ffmpeg',
            '-i', input_video_path,       # Input file
            '-map', f'0:a:{channel}',     # Selecting the specific audio stream
            '-c:a', 'copy',               # Copying the audio codec (no encoding)
            output_audio_path             # Output file
        ]
        subprocess.run(command, check=True)
        print(f"Audio channel {channel + 1} extracted to '{output_audio_path}' successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

# Function to parse the file name for language and channel info
def parse_filename_for_language(filename):
    # Regex pattern to match language and channel info
    pattern = r"_(\d)([A-Z]+)\.[^\.]+$"
    matches = re.findall(pattern, filename, re.IGNORECASE)
    return [(int(channel), lang.upper()) for channel, lang in matches]

# Function to map language codes to full names
def map_language_code_to_name(lang_code):
    mapping = {
        "RUS": "Russian",
        "RU": "Russian",
        "UKR": "Ukraine",
        "UK": "Ukraine",
        "ENG": "English",
        "EN": "English"
    }
    return mapping.get(lang_code.upper(), "Unknown")

# Watching folders and processing files with root directory
def watch_and_process_multilang(root_folder, extensions, supported_langs = ["Russian", "English", "Ukrainian"]):
    for ext in extensions:
        for video_file in glob.glob(f"{root_folder}/*.{ext}"):
            if is_file_ready(video_file):
                language_info = parse_filename_for_language(os.path.basename(video_file))
                for channel, lang_code in language_info:
                    lang_name = map_language_code_to_name(lang_code)
                    if lang_name in supported_langs:

                        ext = get_audio_extension(get_audio_codec(video_file))
                        output_audio_path = f"{video_file.rsplit('.', 1)[0]}_{channel}channel_{lang_name}.{ext}"
                        extract_audio(video_file, output_audio_path, channel - 1)
                        print(f"Extracted {lang_name} audio to {output_audio_path}")
                os.remove(video_file)
                print(f"Everything is extracted. {video_file} is deleted.")



def main():
    parser = argparse.ArgumentParser(description='Process some videos.')
    parser.add_argument("-d", "--directory", default=".", type=str, help='Root folder to search for video files')
    parser.add_argument("-m", "--multilang", default=".", type=str, help='Root folder to search for video files with multilang tracks (name of file must be _1UKR_2ENG.avi or _3RUS.mxf)')

    args = parser.parse_args()

    directory = args.directory
    multilang = args.multilang
    folders_to_watch = ['1ch', '2ch', '3ch', '4ch', '5ch', '6ch']
    video_extensions = ['mp4', 'mkv', 'avi', 'aac', 'mp3']
    print(f"In {directory} in folders {', '.join(folders_to_watch)} lok for {', '.join(video_extensions)}")

    while True:
        print(f"Watch and process directory {directory}")
        watch_and_process(directory, folders_to_watch, video_extensions)
        watch_and_process_multilang(multilang, video_extensions)
        time.sleep(10)

if __name__ == "__main__":
    main()
