@echo off

set STYLE=anime_style
rem STYLE=opensketch_style
set RGB_PATH=input
set DEPTH_PATH=output
set RESULT_PATH=results\%STYLE%
set MAX_FRAMES=999
set RENDER_RES=480

rmdir /s /q %RESULT_PATH%
python encoder.py --name %STYLE% --dataroot %RGB_PATH% --how_many %MAX_FRAMES% --size %RENDER_RES%

@pause