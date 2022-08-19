@echo off

cd %dp~1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg

%FFMPEG_PATH% -y -i output\output%%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r 30 output\output.mp4

@pause
