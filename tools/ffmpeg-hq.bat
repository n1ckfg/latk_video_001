@echo off

cd %dp~1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg
set TARGET_DIR="..\output"

%FFMPEG_PATH% -y -i %TARGET_DIR%\output%%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 7 -r 30 %TARGET_DIR%\output.mp4

@pause
