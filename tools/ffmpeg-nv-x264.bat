@echo off

cd %~dp1

set FFMPEG_PATH=C:\util\ffmpeg\bin\ffmpeg
set TARGET_DIR="..\output"

%FFMPEG_PATH% -y -i %TARGET_DIR%\output%%d.png -r 30 -c:v h264_nvenc -pix_fmt yuvj444p -profile:v high -tune hq -rc-lookahead 8 -bf 2 -rc vbr -cq 26 -b:v 0 -maxrate 120M -bufsize 240M %TARGET_DIR%\output.mp4

@pause
