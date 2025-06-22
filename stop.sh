#!/bin/bash

# Configuration
PIDFILE="comfyui-server.pid"
SYSLOG_TAG="comfyui-server"

# Function to log to syslog with fallback
log_message() {
    local message="$1"
    local priority="$2"
    
    if command -v logger >/dev/null 2>&1; then
        echo "$message" | logger -t "$SYSLOG_TAG" ${priority:+-p "$priority"}
    elif [ -w /dev/log ]; then
        echo "<6>$SYSLOG_TAG: $message" > /dev/log
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$SYSLOG_TAG] $message" >> "comfyui-server.log"
    fi
}

# Stop server using PID file if available
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping ComfyUI server with PID $PID..."
        log_message "Stopping ComfyUI server with PID $PID" "info"
        
        # Try graceful shutdown first
        kill -TERM "$PID"
        sleep 5
        
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force killing server..."
            log_message "Force killing ComfyUI server with PID $PID" "warning"
            kill -KILL "$PID"
        fi
        
        rm -f "$PIDFILE"
        log_message "ComfyUI server stopped" "info"
        echo "ComfyUI server stopped"
    else
        echo "Process with PID $PID is not running"
        rm -f "$PIDFILE"
    fi
else
    echo "No PID file found, trying to stop by process name..."
    log_message "Stopping ComfyUI server by process name (no PID file)" "info"
    
    # Stop all uvicorn processes running main:app (on any port)
    PIDS=$(ps aux | grep 'python3.*main.py' | grep -v grep | awk '{print $2}')
    
    if [ -n "$PIDS" ]; then
        echo "Found running processes: $PIDS"
        echo "$PIDS" | xargs -r kill -TERM
        sleep 5
        
        # Force kill if any still running
        REMAINING=$(ps aux | grep 'python3.*main.py' | grep -v grep | awk '{print $2}')
        if [ -n "$REMAINING" ]; then
            echo "Force killing remaining processes: $REMAINING"
            echo "$REMAINING" | xargs -r kill -KILL
        fi
        
        log_message "ComfyUI server processes stopped" "info"
        echo "ComfyUI server stopped"
    else
        echo "No running ComfyUI server found"
    fi
fi
