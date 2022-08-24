ffmpeg -y -i output/output%%d.png -c:v libx264 -pix_fmt yuvj444p -preset slow -crf 0 -r 30 output/output.mp4
