import asyncio
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("subtitles_log_async.log"), logging.StreamHandler()])

# Asynchronously run a command line process
async def run_command_line(cmd):
    proc = await asyncio.create_subprocess_shell(cmd,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    return proc.returncode, stdout.decode(), stderr.decode()

# Asynchronously transcribe a file
async def transcribe_file(filepath, language, delete_files, semaphore):
    async with semaphore:  # Use the semaphore to limit concurrency
        srt_file = filepath.with_suffix('.srt')
        if srt_file.exists():
            logging.warning(f"Skipping {filepath} as SRT already exists.")
            return

        cmd = f'start cmd.exe /k whisper --model large-v3 "{filepath}" --output_dir "{filepath.parent}" --output_format srt'
        if language != "AUTO":
            cmd += f" --language {language}"
        cmd += " --device cuda"

        returncode, _, stderr = await run_command_line(cmd)
        if returncode == 0:
            logging.info(f"Successfully transcribed {filepath}.")
            if delete_files:
                filepath.unlink()
                logging.info(f"Deleted {filepath}.")
        else:
            logging.error(f"Failed to transcribe {filepath}: {stderr}")

async def transcribe_directory(directory, extensions, language, delete_files, max_concurrent):
    semaphore = asyncio.Semaphore(max_concurrent)  # Control concurrency with a semaphore
    tasks = []
    for ext in extensions:
        for filepath in Path(directory).rglob(f'*.{ext}'):
            task = asyncio.create_task(transcribe_file(filepath, language, delete_files == "Y", semaphore))
            tasks.append(task)
    await asyncio.gather(*tasks)

# Parse command line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Async Video File Transcription Script")
    parser.add_argument("-d", "--dir_path", default=".", help="Directory path for files")
    parser.add_argument("-e", "--extensions", default="ts,mp4,mkv,mxf,avi,mp3,wav,aac",
                        help="File extensions to transcribe, comma-separated")
    parser.add_argument("-df", "--delete_files", choices=["Y", "N"], default="N",
                        help="Delete files after transcribing (Y/N)")
    parser.add_argument("-l", "--language", default="AUTO", help="Transcription language")
    parser.add_argument("-m", "--max_concurrent", type=int, default=2,
                        help="Maximum number of concurrent Whisper subprocesses")
    return parser.parse_args()


# Main async function to orchestrate the transcription process
async def main_async():
    args = parse_arguments()
    await transcribe_directory(
        args.dir_path,
        args.extensions.split(","),
        args.language,
        args.delete_files,
        args.max_concurrent
    )


if __name__ == "__main__":
    asyncio.run(main_async())
