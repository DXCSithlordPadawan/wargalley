#!/bin/bash
echo "Initializing War Galley Digital Engine..."
mkdir -p assets analytics
python3 src/asset_gen.py
podman-compose up -d
echo "Server live at http://localhost:5000"