@echo off

set INPUT_PATH=input
set OUTPUT_PATH=output

del %INPUT_PATH%\*_resampled.ply
rmdir /s /q %OUTPUT_PATH%
mkdir %OUTPUT_PATH%
python encoder.py -- %INPUT_PATH% %OUTPUT_PATH%

@pause