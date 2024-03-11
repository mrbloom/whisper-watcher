import re

def read_srt_file(file_path):
    """Reads the contents of an SRT file into a list of lines."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.readlines()


def parse_srt_contents(srt_content):
    """Parses the list of lines into subtitles with indices, timings, and text."""
    subtitles = []
    subtitle = {'index': '', 'time': '', 'text': ''}
    for line in srt_content:
        line = line.strip()
        if line.isdigit():
            if subtitle['index']:  # If there's already a subtitle, append it before starting a new one
                subtitles.append(subtitle)
                subtitle = {'index': '', 'time': '', 'text': ''}
            subtitle['index'] = line
        elif re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
            subtitle['time'] = line
        elif line == "" and subtitle['text']:  # Only append if there's accumulated text
            subtitles.append(subtitle)
            subtitle = {'index': '', 'time': '', 'text': ''}
        else:
            subtitle['text'] += (line + " ") if subtitle['text'] else line
    if subtitle['text']:  # Ensure the last subtitle is added if not empty
        subtitles.append(subtitle)
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
    i=1
    for current_subtitle, next_subtitle in zip(subtitles, subtitles[1:]):
        current_text = current_subtitle['text'].strip()
        next_text = next_subtitle['text'].strip()
        print(i)
        if current_text == next_text:
            # If the current subtitle text is equal to the next, update the stop time of the last subtitle in deduplicated list
            deduplicated[-1]['time'] = deduplicated[-1]['time'].split(' --> ')[0] + ' --> ' + \
                                       next_subtitle['time'].split(' --> ')[1]
            print(f"duplicate was '{current_text}'")
        else:
            # If not a duplicate, add the next subtitle to the deduplicated list
            if deduplicated[-1]['text'].strip() != next_text:
                deduplicated.append(next_subtitle)
        i+=1

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
file_path = r'../srt/SIMVOL_VOLYA.srt'
srt_content = read_srt_file(file_path)
parsed_subtitles = parse_srt_contents(srt_content)
deduplicated_subtitles = deduplicate_subtitles(parsed_subtitles)
cleaned_content = generate_cleaned_srt_content(deduplicated_subtitles)
output_file_path = r'../srt/SIMVOL_VOLYA_out.srt'
write_srt_file(output_file_path, cleaned_content)




