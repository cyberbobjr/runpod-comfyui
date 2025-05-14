#!/bin/bash
# Pour lancer en tâche de fond (background) et écrire les logs dans un fichier :
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8081 > server.log 2>&1 &
