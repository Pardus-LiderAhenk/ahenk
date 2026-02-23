#!/bin/bash

# Default file name for policy
DEFAULT_FILE_NAME="99-block-storage.rules"

# file nane for task
FILE_NAME="${1:-$DEFAULT_FILE_NAME}"

rm -f /etc/udev/rules.d/$FILE_NAME
udevadm control --reload-rules

udevadm trigger --subsystem-match=usb
udevadm trigger --action=add