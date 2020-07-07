#!/bin/bash

if [ ! -f "capture.webm" ]
then
echo "Source file not found!"
exit 1
fi

# Convert to MP4
if [ ! -f "converted.mp4" ]
then
ffmpeg -i capture.webm converted.mp4
else
echo "MP4 conversion skipped..."
fi

# Crop
if [ ! -f "cropped.mp4" ]
then
ffmpeg -i converted.mp4 -filter:v "crop=840:900:30:90" -c:a copy cropped.mp4
else
echo "Cropping skipped..."
fi

# Reduce resolution
if [ ! -f "small.mp4" ]
then
ffmpeg -i cropped.mp4 -vf scale=560:-1 small.mp4
else
echo "Resizing skipped..."
fi

# Reduce frame rate
if [ ! -f "lowfr.mp4" ]
then
ffmpeg -i small.mp4 -filter:v fps=fps=10 lowfr.mp4
else
echo "Frame rate reduction skipped..."
fi

# Clip
if [ ! -f "clipped.mp4" ]
then
ffmpeg -ss 00:00:01.500 -i lowfr.mp4 -t 00:00:14.000 -c copy clipped.mp4
else
echo "Clipping skipped..."
fi
