Write-Host "Initializing War Galley Digital Engine..."
New-Item -ItemType Directory -Force -Path assets | Out-Null
New-Item -ItemType Directory -Force -Path analytics | Out-Null

# Install Python dependencies
pip install -r requirements.txt

# Generate visual assets
python src\asset_gen.py

# Start the game server directly (no container required)
Write-Host "Server starting at http://localhost:5000"
python src\server.py
