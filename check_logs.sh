#!/bin/bash

# Configuration
SYSLOG_TAG="comfyui-server"
LOGFILE="comfyui-server.log"
PIDFILE="comfyui-server.pid"

echo "=== ComfyUI Server Log Checker ==="
echo

# Check if server is running
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✓ Server is running with PID: $PID"
    else
        echo "✗ PID file exists but process is not running"
        echo "  Consider removing $PIDFILE"
    fi
else
    echo "✗ Server is not running (no PID file)"
fi

echo

# Check logging capabilities
echo "=== Logging Configuration ==="

# Check logger command
if command -v logger >/dev/null 2>&1; then
    echo "✓ 'logger' command is available"
    
    # Test logger
    if logger -t "$SYSLOG_TAG-test" "Test message from check_logs.sh" 2>/dev/null; then
        echo "✓ 'logger' command works correctly"
    else
        echo "✗ 'logger' command failed"
    fi
else
    echo "✗ 'logger' command is not available"
fi

# Check /dev/log
if [ -w /dev/log ]; then
    echo "✓ /dev/log is writable (direct syslog available)"
else
    echo "✗ /dev/log is not writable"
fi

# Check journalctl
if command -v journalctl >/dev/null 2>&1; then
    echo "✓ 'journalctl' is available (systemd logging)"
else
    echo "✗ 'journalctl' is not available"
fi

echo

# Check log files
echo "=== Log Files ==="

if [ -f "$LOGFILE" ]; then
    SIZE=$(stat -c%s "$LOGFILE" 2>/dev/null || echo "unknown")
    LINES=$(wc -l < "$LOGFILE" 2>/dev/null || echo "unknown")
    echo "✓ Local log file exists: $LOGFILE"
    echo "  Size: $SIZE bytes"
    echo "  Lines: $LINES"
    
    echo "  Last 5 lines:"
    tail -5 "$LOGFILE" | sed 's/^/    /'
else
    echo "✗ Local log file not found: $LOGFILE"
fi

echo

# Check syslog
echo "=== Syslog Messages ==="

# Try different methods to read syslog
if command -v journalctl >/dev/null 2>&1; then
    echo "Recent messages from journalctl:"
    journalctl -t "$SYSLOG_TAG" --no-pager -n 5 2>/dev/null | sed 's/^/  /' || echo "  No messages found"
elif [ -r /var/log/syslog ]; then
    echo "Recent messages from /var/log/syslog:"
    grep "$SYSLOG_TAG" /var/log/syslog | tail -5 | sed 's/^/  /' || echo "  No messages found"
elif [ -r /var/log/messages ]; then
    echo "Recent messages from /var/log/messages:"
    grep "$SYSLOG_TAG" /var/log/messages | tail -5 | sed 's/^/  /' || echo "  No messages found"
else
    echo "Cannot access system log files"
fi

echo

# Provide recommendations
echo "=== Recommendations ==="

if ! command -v logger >/dev/null 2>&1 && [ ! -w /dev/log ]; then
    echo "⚠ Neither 'logger' nor '/dev/log' is available"
    echo "  Logs will only be written to local file: $LOGFILE"
    echo "  Consider installing 'logger' or configuring syslog"
fi

if command -v journalctl >/dev/null 2>&1; then
    echo "ℹ To follow live logs: journalctl -t $SYSLOG_TAG -f"
elif [ -r /var/log/syslog ]; then
    echo "ℹ To follow live logs: tail -f /var/log/syslog | grep $SYSLOG_TAG"
fi

echo "ℹ To follow local logs: tail -f $LOGFILE"

echo
echo "=== Usage ==="
echo "Start server: ./start.sh"
echo "Stop server:  ./stop.sh"
echo "Check logs:   ./check_logs.sh"
