@echo off
echo Initializing War Galley Digital Engine...
mkdir assets 2>nul
mkdir analytics 2>nul

REM Install Python dependencies
pip install --prefer-binary --quiet -r requirements.txt

REM Generate visual assets
python src\asset_gen.py

REM Start the game server directly (no container required)
echo Server starting at http://localhost:5000
echo.
echo Once the server is ready, open a second terminal and run:
echo   python src\client.py
echo.
python src\server.py
