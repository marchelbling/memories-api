#!/bin/bash -e

pip install -r /api/requirements.txt
cd /api/memories && gunicorn -b 0.0.0.0:8000 app:app
