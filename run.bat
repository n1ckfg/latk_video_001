@echo off

set INPUT_PATH=input
set OUTPUT_PATH=output
set DIM=1024
set TILE_PIXEL_SIZE=8
set TILE_SUBDIV=16

del %INPUT_PATH%\*_resampled.ply
rmdir /s /q %OUTPUT_PATH%
mkdir %OUTPUT_PATH%
python encoder.py -- %INPUT_PATH% %OUTPUT_PATH% %DIM% %TILE_PIXEL_SIZE% %TILE_SUBDIV%

@pause