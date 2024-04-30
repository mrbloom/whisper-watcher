set dir_path="Z:\whisper"
set extensions="ts,mp4,mkv,mxf,avi,mp3,wav,aac"
set delete_files=Y
set language=AUTO

set background_mask="Z:\RussiaContentRecords\2024\2024_*\2024_*_*\*\"
set background_language=Russian
set background_delete=N

python .\make_srt_files.py -d %dir_path% -e %extensions% -df %delete_files% -l %language% -bl %background_language% -bd %background_delete% -bm %background_mask%