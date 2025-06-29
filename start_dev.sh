#!/bin/bash
LOGFILE="comfyui-server.log"
MAXSIZE=10485760 # 10 Mo

if [ -f "$LOGFILE" ] && [ $(stat -c%s "$LOGFILE") -ge $MAXSIZE ]; then
    mv "$LOGFILE" "$LOGFILE.1"
    [ -f "$LOGFILE.1" ] && mv "$LOGFILE.1" "$LOGFILE.2"
    [ -f "$LOGFILE.2" ] && mv "$LOGFILE.2" "$LOGFILE.3"
fi

# nohup python -m uvicorn main:app --reload --host 0.0.0.0 --port 8081 >> "$LOGFILE" 2>&1 &
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8082
