#!/bin/sh

if [ "$ENV" = "dev" ]; then
  exec python3 -u app.py
else
  exec gunicorn -b 0.0.0.0:5000 app:app
fi
