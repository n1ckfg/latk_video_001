STYLE=anime_style
#STYLE=opensketch_style
RGB_PATH=input
DEPTH_PATH=output
RESULT_PATH=results/$STYLE
MAX_FRAMES=9999
RENDER_RES=480 # 480

rm -rf $RESULT_PATH
python test.py --name $STYLE --dataroot $RGB_PATH --how_many $MAX_FRAMES --size $RENDER_RES

if [ "$1" = "midas" ]
then
	echo ""
	echo "+ + +   MiDaS pass enabled...   + + +"
	rm -rf $DEPTH_PATH
	python midas/run.py --input_path $RGB_PATH --output_path $DEPTH_PATH --model_weights midas/model/model-f6b98070.pt 
fi

LINE_THRESHOLD=64 # 64
USE_SWIG=1
INPAINT=0

if [ "$1" = "inpaint" ]
then
	echo ""
	echo "+ + +   Inpainting pass enabled...   + + +"
	INPAINT=1
fi

python skeletonizer.py -- $RESULT_PATH $RGB_PATH $DEPTH_PATH $LINE_THRESHOLD $USE_SWIG $INPAINT

