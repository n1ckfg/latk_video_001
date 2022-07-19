INPUT_PATH=input
OUTPUT_PATH=output

rm $INPUT_PATH/*_resampled.ply
rm -rf $OUTPUT_PATH
mkdir $OUTPUT_PATH
python encoder.py -- $INPUT_PATH $OUTPUT_PATH

