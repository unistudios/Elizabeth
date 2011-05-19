#!/bin/bash
# Kill Django.  Ghetto!

pid=$(ps -ef | grep manage.py | head -1 | awk '{print $2}')
kill -9 $pid
