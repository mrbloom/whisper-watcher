set dir_path="Z:\fast_channels\OTERRA\TRANSCRIBE_DRAFT"
set extensions="ts,mp4,mkv,mxf,avi,mp3,wav,aac"
set delete_files=N
set language=Ukrainian
set task=transcribe
set model=large-v2

set background_mask="Z:\RussiaContentRecords\2024\2024_*\2024_*_*\*\"
set background_language=Russian
set background_delete=N

python .\make_srt_files_ottera.py -m %model% -d %dir_path% -e %extensions% -df %delete_files% -l %language% -t %task% -bl %background_language% -bd %background_delete% -bm %background_mask%