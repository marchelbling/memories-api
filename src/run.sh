#!/bin/bash -e

pip install -r /api/requirements.txt
cd /api/src && gunicorn -b 0.0.0.0:8000 search:app
