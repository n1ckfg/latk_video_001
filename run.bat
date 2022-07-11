@echo off

set STYLE=anime_style
rem STYLE=opensketch_style
set RGB_PATH=input
set DEPTH_PATH=output
set RESULT_PATH=results\%STYLE%
set MAX_FRAMES=999
set RENDER_RES=480

rmdir /s /q %RESULT_PATH%
python test.py --name %STYLE% --dataroot %RGB_PATH% --how_many %MAX_FRAMES% --size %RENDER_RES%

rem rmdir /s /q %DEPTH_PATH%
rem python midas\run.py --input_path %RGB_PATH% --output_path %DEPTH_PATH% --model_weights midas\model\model-f6b98070.pt 

set LINE_THRESHOLD=64
set USE_SWIG=0
set INPAINT=0

python skeletonizer.py -- %RESULT_PATH% %RGB_PATH% %DEPTH_PATH% %LINE_THRESHOLD% %USE_SWIG% %INPAINT%

@pause