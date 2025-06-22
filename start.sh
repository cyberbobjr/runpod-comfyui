#!/bin/bash
LOGFILE="comfyui-server.log"
MAXSIZE=10485760 # 10 Mo

if [ -f "$LOGFILE" ] && [ $(stat -c%s "$LOGFILE") -ge $MAXSIZE ]; then
    mv "$LOGFILE" "$LOGFILE.1"
    [ -f "$LOGFILE.1" ] && mv "$LOGFILE.1" "$LOGFILE.2"
    [ -f "$LOGFILE.2" ] && mv "$LOGFILE.2" "$LOGFILE.3"
fi

nohup bash -c 'python3 -u main.py 2>&1 | while IFS= read -r line; do
    logger -t "comfyui-server" "$line"
done' &

echo "ComfyUI server started in background with PID $!"
echo "Logs are being sent to syslog with tag 'comfyui-server'"
echo "Use 'journalctl -t comfyui-server -f' to follow logs"