#!/bin/bash

# Default file name for policy
DEFAULT_FILE_NAME="99-block-webcam.rules"

# file nane for task
FILE_NAME="${1:-$DEFAULT_FILE_NAME}"

echo 'ACTION=="add|change", SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="0e", ATTR{authorized}="0"
ACTION=="add|change", SUBSYSTEM=="usb", ENV{ID_USB_INTERFACES}=="*:0e:*", ATTR{authorized}="0"
' > /etc/udev/rules.d/$FILE_NAME

udevadm control --reload-rules

for device in /sys/bus/usb/devices/*; do
    if [ -e "$device/bInterfaceClass" ]; then
        cls=$(cat "$device/bInterfaceClass")
        if [ "$cls" == "0e" ]; then
             echo 0 > "$device/authorized" 2>/dev/null
             parent=${device%%:*}
             if [ -e "$parent/authorized" ]; then
                 echo 0 > "$parent/authorized" 2>/dev/null
             fi
        fi
    fi
done