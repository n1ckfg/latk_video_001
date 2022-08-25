TARGET_DIR="../output"

ffmpeg -y -i $TARGET_DIR/output%d.png -c:v libx264 -pix_fmt yuvj444p -preset slow -crf 0 -r 30 $TARGET_DIR/output.mp4
