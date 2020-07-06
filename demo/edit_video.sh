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
echo "MP4 conversion is skipped..."
fi

# Crop
if [ ! -f "cropped.mp4" ]
then
ffmpeg -i converted.mp4 -filter:v "crop=900:600:50:80" -c:a copy cropped.mp4
else
echo "Cropping is skipped..."
fi
