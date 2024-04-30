set dir_path="Z:\whisper"
set extensions="ts,mp4,mkv,mxf,avi,mp3,wav,aac"
set delete_files=Y
set language=AUTO

@REM set background_mask="Z:\RussiaContentRecords\2024\2024_*\2024_*_*\*\"
@REM set background_language=Russian
@REM set background_delete=N

python .\make_srt_files_funct.py -d %dir_path% -e %extensions% -df %delete_files% -l %language%

@REM -bl %background_language% -bd %background_delete% -bm %background_mask%