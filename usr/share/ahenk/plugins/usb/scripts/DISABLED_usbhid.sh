#!/bin/bash

# Default file name for policy
DEFAULT_FILE_NAME="99-block-hid.rules"

# file nane for task
FILE_NAME="${1:-$DEFAULT_FILE_NAME}"

echo 'ACTION=="add|change", SUBSYSTEM=="usb", ATTR{bInterfaceClass}=="03", ATTR{authorized}="0"
ACTION=="add|change", SUBSYSTEM=="usb", ENV{ID_USB_INTERFACES}=="*:03:*", ATTR{authorized}="0"
' > /etc/udev/rules.d/$FILE_NAME

udevadm control --reload-rules

for device in /sys/bus/usb/devices/*; do
    if [ -e "$device/bInterfaceClass" ]; then
        cls=$(cat "$device/bInterfaceClass")
        if [ "$cls" == "03" ]; then
             echo 0 > "$device/authorized" 2>/dev/null
             parent=${device%%:*}
             if [ -e "$parent/authorized" ]; then
                 echo 0 > "$parent/authorized" 2>/dev/null
             fi
        fi
    fi
done