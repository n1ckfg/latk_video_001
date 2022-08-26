@echo off

cd %dp~1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg
set TARGET_DIR="..\output"

%FFMPEG_PATH% -y -i %TARGET_DIR%\output%%d.png -c:v libx265 -vtag hvc1 -preset slow -crf 17 -r 30 %TARGET_DIR%\output.mp4

@pause
