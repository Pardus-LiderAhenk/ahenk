#!/bin/bash
var=$(lsmod | awk '{print $1}'| grep usblp)

service cups stop

if [ -z "$var" ]
then
echo "USB printer devices are already blocked"
else
rmmod usblp
sleep 2
fi

