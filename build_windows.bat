@echo off
echo Building War Galley standalone Windows executable...

REM Install build dependencies
pip install --quiet pyinstaller

REM Install runtime dependencies
pip install --quiet -r requirements.txt

REM Generate assets before packaging
python src\asset_gen.py

REM Build the standalone executable
pyinstaller wargalley.spec --clean --noconfirm

echo.
echo Build complete. Executable is in: dist\wargalley\wargalley.exe
echo To launch without Python: dist\wargalley\wargalley.exe
