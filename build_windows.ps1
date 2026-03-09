Write-Host "Building War Galley standalone Windows executable..."

# Install build dependencies
pip install pyinstaller

# Install runtime dependencies
pip install -r requirements.txt

# Generate assets before packaging
python src\asset_gen.py

# Build the standalone executable
pyinstaller wargalley.spec --clean --noconfirm

Write-Host ""
Write-Host "Build complete. Executable is in: dist\wargalley\wargalley.exe"
Write-Host "To launch without Python: dist\wargalley\wargalley.exe"
