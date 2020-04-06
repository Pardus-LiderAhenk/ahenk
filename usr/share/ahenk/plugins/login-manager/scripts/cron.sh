#!/bin/bash
#write out current crontab
crontab -l > cron
#new cron into cron file
echo "$1" >> cron
#install new cron file
crontab cron
rm cron