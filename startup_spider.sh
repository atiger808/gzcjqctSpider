#!/bin/bash

# ps -aux|grep gzcjs_spider|grep -v grep|awk '{print $2}'|xargs kill -9
ps -aux|grep gunicorn|grep "app:app"|grep -v grep|awk '{print $2}'|xargs kill -9
ps -aux|grep "gzcjqctSpider/app"|grep -v grep|awk '{print $2}'|xargs kill -9
cd /www/home/gzcjqctSpider
nohup /root/anaconda3/envs/gpfspider/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app:app >> /var/log/spider.log 2>&1 &
# nohup /www/home/gzcjqct_spider/app >> /var/log/spider.log 2>&1 &

