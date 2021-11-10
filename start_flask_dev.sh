#!/bin/bash
echo $PWD
# The /opt/crawler_venv path matches the setup in Dockerfile
source "/opt/crawler_venv/bin/activate"
# Start the application
python app.py
