# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ["../src/main.py"],
    pathex=["D:\\new-manga-graphic"],
    binaries=[],
    datas=[
        ("C:\\Users\\Rafael\\Anaconda3\\lib\\site-packages\\eel\\eel.js", "eel"),
        ("../src/public", "public"),
    ],
    hiddenimports=["bottle_websocket", "appdirs"],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
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
    name="mangafetch",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon="../icons/icon.ico",
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="main",
)
