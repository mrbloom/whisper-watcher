import whisper

model = whisper.load_model("large-v3")
result = model.transcribe(r"D:\soft\whisper-watcher\videos\1.mp4")
print(result["text"])


# import tkinter as tk
# from tkinter import ttk, messagebox
# from tkinter import scrolledtext  # Corrected import
# import threading
# import whisper
# import os
# from queue import Queue
#
#
# def change_file_extension(file_path, new_extension):
#     # Split the file path into root and extension
#     root, _ = os.path.splitext(file_path)
#     # Ensure the new extension starts with a dot
#     if not new_extension.startswith('.'):
#         new_extension = '.' + new_extension
#     # Construct the new file path with the new extension
#     new_file_path = root + new_extension
#     return new_file_path
#
#
# def transcribe_with_whisper(file_path, language='english', model_name="large-v3", text_widget=None):
#     try:
#         # Initialize the model
#         model = whisper.load_model(model_name)
#
#         # Transcribe the audio file
#         result = model.transcribe(file_path, language=language)
#
#         # Save the transcription to an SRT file
#         srt_file_path = os.path.splitext(file_path)[0] + '.srt'
#         transcription_text = ""
#         with open(srt_file_path, "w") as srt_file:
#             for i, segment in enumerate(result["segments"]):
#                 start = segment["start"]
#                 end = segment["end"]
#                 text = segment["text"]
#                 srt_file.write(f"{i+1}\n")
#                 srt_file.write(f"{whisper.utils.format_timestamp(start)} --> {whisper.utils.format_timestamp(end)}\n")
#                 srt_file.write(f"{text}\n\n")
#                 transcription_text += f"{text}\n"
#
#         if text_widget:
#             text_widget.insert(tk.END, f"Transcription for {os.path.basename(file_path)}:\n{transcription_text}\n")
#             text_widget.insert(tk.END, "-"*80 + "\n")
#             text_widget.yview(tk.END)
#
#         print(f"Transcription saved to {srt_file_path}")
#     except Exception as e:
#         if text_widget:
#             text_widget.insert(tk.END, f"Error transcribing file {file_path}: {e}\n")
#             text_widget.yview(tk.END)
#         print(f"Error transcribing file {file_path}: {e}")
#
# def worker(task_queue, language, delete_files, text_widget):
#     while not task_queue.empty():
#         file_path = task_queue.get()
#         transcribe_with_whisper(file_path, language=language, text_widget=text_widget)
#         if delete_files:
#             os.remove(file_path)
#             print(f"Deleted file: {file_path}")
#         task_queue.task_done()
#
# def start_transcription(directory, extensions, language, delete_files, num_streams, text_widget):
#     files = [os.path.join(directory, f) for f in os.listdir(directory) if any(f.endswith(ext) for ext in extensions.split(','))]
#     task_queue = Queue()
#     for file in files:
#         task_queue.put(file)
#
#     for _ in range(min(num_streams, task_queue.qsize())):
#         threading.Thread(target=worker, args=(task_queue, language, delete_files, text_widget)).start()
#
#
#
# def create_gui():
#     root = tk.Tk()
#     root.title("Video Transcription")
#
#     # Directory Path
#     tk.Label(root, text="Directory Path:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
#     dir_path = tk.Entry(root, width=50)
#     dir_path.grid(row=0, column=1, padx=10, pady=5)
#
#     # File Extensions
#     tk.Label(root, text="Extensions (comma separated):").grid(row=1, column=0, padx=10, pady=5, sticky="w")
#     extensions = tk.Entry(root, width=50)
#     extensions.grid(row=1, column=1, padx=10, pady=5)
#     extensions.insert(0, "ts,mp4,mkv,mxf,wav,mp3,aac")  # Default value
#
#     # Language Selection
#     tk.Label(root, text="Language:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
#     language = ttk.Combobox(root, values=["English", "Russian", "Ukrainian"], width=47)
#     language.grid(row=2, column=1, padx=10, pady=5)
#     language.set("English")  # Default value
#
#     # Delete Files Checkbox
#     delete_files_var = tk.BooleanVar()
#     delete_files = tk.Checkbutton(root, text="Delete files after transcription", variable=delete_files_var)
#     delete_files.grid(row=3, column=1, padx=10, pady=5, sticky="w")
#
#     # Parallel Streams Selection
#     tk.Label(root, text="Number of Parallel Streams:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
#     num_streams = tk.Spinbox(root, from_=1, to=10, width=48)
#     num_streams.grid(row=5, column=1, padx=10, pady=5)
#
#     # Transcription Text Display
#     tk.Label(root, text="Transcriptions:").grid(row=6, column=0, padx=10, pady=5, sticky="nw")
#     transcription_text = scrolledtext.ScrolledText(root, height=10, width=75)
#     transcription_text.grid(row=6, column=1, padx=10, pady=5, sticky="we")
#
#     # Start Button
#     start_btn = tk.Button(root, text="Start Transcription",
#                           command=lambda: threading.Thread(target=start_transcription, args=(
#                               dir_path.get(),
#                               extensions.get(),
#                               language.get(),
#                               delete_files_var.get(),
#                               int(num_streams.get()),
#                               transcription_text
#                           )).start())
#     start_btn.grid(row=4, column=1, padx=10, pady=10, sticky="e")
#
#     root.mainloop()
#
#
# if __name__ == "__main__":
#     create_gui()
