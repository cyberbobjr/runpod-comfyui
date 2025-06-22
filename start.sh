#!/bin/bash

# Configuration
LOGFILE="comfyui-server.log"
MAXSIZE=10485760 # 10 Mo
SYSLOG_TAG="comfyui-server"
PIDFILE="comfyui-server.pid"

# Function to log to syslog with fallback to file
log_message() {
    local message="$1"
    local priority="$2"
    
    # Try to use logger first
    if command -v logger >/dev/null 2>&1; then
        echo "$message" | logger -t "$SYSLOG_TAG" ${priority:+-p "$priority"}
    else
        # Fallback to direct syslog if available
        if [ -w /dev/log ]; then
            echo "<6>$SYSLOG_TAG: $message" > /dev/log
        else
            # Final fallback to file logging
            echo "$(date '+%Y-%m-%d %H:%M:%S') [$SYSLOG_TAG] $message" >> "$LOGFILE"
        fi
    fi
}

# Rotate log files if needed
if [ -f "$LOGFILE" ] && [ $(stat -c%s "$LOGFILE") -ge $MAXSIZE ]; then
    [ -f "$LOGFILE.2" ] && mv "$LOGFILE.2" "$LOGFILE.3"
    [ -f "$LOGFILE.1" ] && mv "$LOGFILE.1" "$LOGFILE.2"
    mv "$LOGFILE" "$LOGFILE.1"
fi

# Check if server is already running
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    echo "ComfyUI server is already running with PID $(cat "$PIDFILE")"
    exit 1
fi

# Start the server with improved logging
{
    python3 -u main.py 2>&1 | while IFS= read -r line; do
        # Send to syslog with timestamp
        log_message "$line" "info"
        # Also keep a local log file as backup
        echo "$(date '+%Y-%m-%d %H:%M:%S') $line" >> "$LOGFILE"
    done
} &

SERVER_PID=$!
echo $SERVER_PID > "$PIDFILE"

log_message "ComfyUI server started with PID $SERVER_PID" "info"
echo "ComfyUI server started in background with PID $SERVER_PID"
echo "PID file: $PIDFILE"
echo "Log file: $LOGFILE"

# Check logging method being used
if command -v logger >/dev/null 2>&1; then
    echo "Logs are being sent to syslog using 'logger' command with tag '$SYSLOG_TAG'"
    echo "Use 'journalctl -t $SYSLOG_TAG -f' to follow syslog logs"
elif [ -w /dev/log ]; then
    echo "Logs are being sent to syslog directly via /dev/log with tag '$SYSLOG_TAG'"
    echo "Use 'tail -f /var/log/syslog | grep $SYSLOG_TAG' to follow logs"
else
    echo "Syslog not available, logs are written to file: $LOGFILE"
    echo "Use 'tail -f $LOGFILE' to follow logs"
fi