import os
import re
from glob import glob


def read_srt_file(file_path):
    """Reads the contents of an SRT file into a list of lines."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


import re


def parse_srt_contents(srt_content):
    """Parses the list of lines into subtitles, ignoring empty subtitles, and reorders indexes."""
    subtitles = []
    subtitle = {'index': '', 'time': '', 'text': ''}
    for line in srt_content:
        line = line.strip()
        match line:
            case _ if line.isdigit():
                # Start a new subtitle if the current has text
                if subtitle['text']:
                    subtitles.append(subtitle)
                    subtitle = {'index': '', 'time': '', 'text': ''}
                subtitle['index'] = line
            case _ if re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
                subtitle['time'] = line
            case "" if subtitle['text']:
                # Append only if there's accumulated text, otherwise ignore
                continue
            case _:
                subtitle['text'] += (line + " ") if subtitle['text'] else line
    # Append the last subtitle if not empty
    if subtitle['text']:
        subtitles.append(subtitle)

    # Remove all subtitles with empty 'text'
    subtitles = [sub for sub in subtitles if sub['text'].strip()]

    # Reorder indexes
    for i, subtitle in enumerate(subtitles, 1):
        subtitle['index'] = str(i)

    return subtitles


def deduplicate_subtitles(subtitles):
    """
    Removes duplicate subtitles that appear in series and merges their timings.

    Assumes that duplicate lines are consecutive.
    """
    if not subtitles:
        return []

    # Initialize with the first subtitle
    deduplicated = [subtitles[0]]

    for current_subtitle, next_subtitle in zip(subtitles, subtitles[1:]):
        current_text = current_subtitle['text'].strip()
        next_text = next_subtitle['text'].strip()
        try:
            if current_text == next_text:
                # If the current subtitle text is equal to the next, update the stop time of the last subtitle in deduplicated list
                deduplicated[-1]['time'] = deduplicated[-1]['time'].split(' --> ')[0] + ' --> ' + \
                                           next_subtitle['time'].split(' --> ')[1]
                print(f"duplicate was '{current_text}'")
            else:
                # If not a duplicate, add the next subtitle to the deduplicated list
                if deduplicated[-1]['text'].strip() != next_text:
                    deduplicated.append(next_subtitle)
        except IndexError as e:
            print(f"Error was {e}")
            print(f"Lines are {current_subtitle}, {next_subtitle}")

    return deduplicated


def generate_cleaned_srt_content(deduplicated_subtitles):
    """Generates the final SRT content from deduplicated subtitles."""
    cleaned_content = []
    for index, subtitle in enumerate(deduplicated_subtitles, start=1):
        cleaned_content.append(f"{index}")
        cleaned_content.append(subtitle['time'])
        cleaned_content.append(subtitle['text'].strip())
        cleaned_content.append("")  # Empty line to separate subtitles
    return cleaned_content

def write_srt_file(file_path, cleaned_content):
    """Writes the cleaned SRT content back to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('\n'.join(cleaned_content))

def make_reduplicate(file_path):
    srt_content = read_srt_file(file_path)
    parsed_subtitles = parse_srt_contents(srt_content)
    deduplicated_subtitles = deduplicate_subtitles(parsed_subtitles)
    cleaned_content = generate_cleaned_srt_content(deduplicated_subtitles)
    output_file_path = file_path
    write_srt_file(output_file_path, cleaned_content)


# Example usage:
# file_path = r'../srt/SIMVOL_VOLYA.srt'
# srt_content = read_srt_file(file_path)
# parsed_subtitles = parse_srt_contents(srt_content)
# deduplicated_subtitles = deduplicate_subtitles(parsed_subtitles)
# cleaned_content = generate_cleaned_srt_content(deduplicated_subtitles)
# output_file_path = r'../srt/SIMVOL_VOLYA_out.srt'
# write_srt_file(output_file_path, cleaned_content)

if __name__ == "__main__":
    folder_path = input("Input folder :")
    for srt in glob(os.path.join(folder_path,"**/*.srt")):
        print(f"Parse srt content for file {srt}")
        make_reduplicate(srt)




