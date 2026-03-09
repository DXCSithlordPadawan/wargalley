Write-Host "Initializing War Galley Digital Engine..."
New-Item -ItemType Directory -Force -Path assets | Out-Null
New-Item -ItemType Directory -Force -Path analytics | Out-Null
python src\asset_gen.py
podman-compose up -d
Write-Host "Server live at http://localhost:5000"
