#!/bin/bash

sed -i 's/\(^.*\)\(locked="[A-Za-z; ]*"\)\(.*$\)/\1\3/' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
