@echo off

cd %dp~1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg
set TARGET_DIR="..\output"

%FFMPEG_PATH% -y -i %TARGET_DIR%\output%%d.png -c:v hevc_nvenc -rc vbr_hq -cq 18 -b:v 0k -2pass 0 -r 30 %TARGET_DIR%\output.mp4

@pause
