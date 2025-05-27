#!/bin/bash
# Pour lancer en tâche de fond (background) et écrire les logs dans un fichier :
# Limite la taille du fichier de log à 10 Mo, conserve 3 archives (logrotate simple via logrotate si dispo)
LOGFILE="comfyui-server.log"
MAXSIZE=10485760 # 10 Mo

# Set COMFYUI_MODEL_DIR only if it doesn't exist
if [ -z "${COMFYUI_MODEL_DIR}" ]; then
    export COMFYUI_MODEL_DIR="/mnt/d/runpod-volume"
fi

if [ -f "$LOGFILE" ] && [ $(stat -c%s "$LOGFILE") -ge $MAXSIZE ]; then
    mv "$LOGFILE" "$LOGFILE.1"
    [ -f "$LOGFILE.1" ] && mv "$LOGFILE.1" "$LOGFILE.2"
    [ -f "$LOGFILE.2" ] && mv "$LOGFILE.2" "$LOGFILE.3"
fi

# nohup uvicorn main:app --reload --host 0.0.0.0 --port 8081 >> "$LOGFILE" 2>&1 &
# nohup uvicorn main:app --reload --host 0.0.0.0 --port 8081
python3 main.py