TARGET_DIR="../output"

ffmpeg -y -i $TARGET_DIR/output%d.png -c:v libx264 -pix_fmt yuv420p -preset slow -crf 17 -r 30 $TARGET_DIR/output.mp4
