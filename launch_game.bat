@echo off
echo Initializing War Galley Digital Engine...
mkdir assets 2>nul
mkdir analytics 2>nul
python src\asset_gen.py
podman-compose up -d
echo Server live at http://localhost:5000
