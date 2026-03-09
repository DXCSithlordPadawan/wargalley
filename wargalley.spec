# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for War Galley Digital Engine — standalone Windows executable.
# Build with:  pyinstaller wargalley.spec
# Output:      dist\wargalley\wargalley.exe

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all hidden imports required by Flask-SocketIO / eventlet / engineio
hidden_imports = (
    collect_submodules("flask")
    + collect_submodules("flask_socketio")
    + collect_submodules("engineio")
    + collect_submodules("socketio")
    + collect_submodules("PIL")
    + collect_submodules("pydantic")
    + collect_submodules("yaml")
    + collect_submodules("numpy")
    + [
        "threading",
        "queue",
        "bidict",
        "dotenv",
    ]
)

# Data files to bundle (scenarios, templates, assets)
datas = (
    collect_data_files("flask")
    + collect_data_files("flask_socketio")
    + collect_data_files("engineio")
    + collect_data_files("socketio")
    + [
        ("scenarios", "scenarios"),
        ("templates", "templates"),
        ("src/engine", "src/engine"),
        ("src/ui", "src/ui"),
        ("src/ai_minimax.py", "src"),
        ("src/asset_gen.py", "src"),
        ("requirements.txt", "."),
    ]
)

a = Analysis(
    ["src/server.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "podman",
        "docker",
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="wargalley",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console window to show server log output
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="wargalley",
)
