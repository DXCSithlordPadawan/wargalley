@echo off
echo Initializing War Galley Digital Engine...
mkdir assets 2>nul
mkdir analytics 2>nul

REM Install Python dependencies
pip install -r requirements.txt

REM Generate visual assets
python src\asset_gen.py

REM Start the game server directly (no container required)
echo Server starting at http://localhost:5000
python src\server.py
