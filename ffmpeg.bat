@echo off

cd %dp~1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg

rem lossless test
%FFMPEG_PATH% -y -i output\output%%d.png -c:v libx264 -pix_fmt yuvj444p -preset slow -crf 0 -r 30 output\output.mp4

rem mobile ready
rem %FFMPEG_PATH% -y -i output\output%%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r 30 output\output.mp4

@pause
