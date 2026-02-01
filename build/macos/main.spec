# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

a = Analysis(
    ['../../main.py'],
    pathex=['../../src'],
    binaries=[],
    datas=[
        ('../../src', 'src'),
        ('../../templates', 'templates'),
    ],
    hiddenimports=[
        'src',
        'src.gui.desktop.main_window',
        'src.converters.markdown_to_docx',
        'src.converters.formula_converter',
        'src.converters.table_converter',
        'src.utils.config',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='Markdown2Academia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../assets/icon.icns' if os.path.exists('../../assets/icon.icns') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Markdown2Academia',
)

app = BUNDLE(
    coll,
    name='Markdown2Academia.app',
    icon='../../assets/icon.icns' if os.path.exists('../../assets/icon.icns') else None,
    bundle_identifier='com.markdown2academia.app',
    info_plist={
        'CFBundleShortVersionString': '0.1.0',
        'CFBundleVersion': '0.1.0',
        'NSHighResolutionCapable': 'True',
    },
)
