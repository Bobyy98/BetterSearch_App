# Import PyInstaller modules
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[os.path.abspath('.')],  # Add your source directory here
    binaries=[],
    datas=[
        ('assets/chevron-down.svg', 'assets'),
        ('assets/your_icon.ico', 'assets'),
        ('dependencies/mft.exe', 'dependencies')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BetterSearchApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon='assets/your_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main'
)
