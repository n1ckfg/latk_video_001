STYLE=anime_style
#STYLE=opensketch_style
RGB_PATH=input
DEPTH_PATH=output
RESULT_PATH=results/$STYLE
MAX_FRAMES=9999
RENDER_RES=480 # 480

rm -rf $RESULT_PATH
python encoder.py --name $STYLE --dataroot $RGB_PATH --how_many $MAX_FRAMES --size $RENDER_RES

