#!/usr/bin/env bash
# Build script for Render deployment
set -o errexit

pip install -r requirements.txt

# Initialize the database and seed with demo data
python seed.py
