#!/bin/bash

sed -n 's/^.*locked="\([A-Za-z0-9; ]*\)".*$/\1/p' /etc/xdg/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml
