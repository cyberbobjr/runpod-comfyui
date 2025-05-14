#!/bin/bash
# Stop all uvicorn processes running main:app (on any port)
ps aux | grep 'uvicorn main:app' | grep -v grep | awk '{print $2}' | xargs -r kill
