#!/bin/bash

# ps -aux|grep gzcjsSpider|grep -v grep|awk '{print $2}'|xargs kill -9
ps -aux|grep gunicorn|grep "app:app"|grep -v grep|awk '{print $2}'|xargs kill -9
ps -aux|grep "gzcjqctSpider/app"|grep -v grep|awk '{print $2}'|xargs kill -9

