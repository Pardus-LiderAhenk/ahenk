#!/bin/bash

var=$(lsof -t /dev/video0)

if [[ -z "$var" ]]
then
echo "Webcam is not in use"
else
kill -9 "$var"
sleep 2
fi

var=$(lsmod | awk '{print $1}'| grep uvcvideo)

if [[ -z "$var" ]]
then
echo "Webcam is already blocked"
else
rmmod uvcvideo
sleep 2
fi


