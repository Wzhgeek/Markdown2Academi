# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import sys
import os

block_cipher = None

a = Analysis(
    ['../../main.py'],
    pathex=['../../src'],
    binaries=[],
    datas=[
        ('../../src', 'src'),
        ('../../templates', 'templates'),
        ('../../assets/icons', 'assets/icons'),
    ],
    hiddenimports=[
        'src',
        'src.gui.desktop.main_window',
        'src.gui.desktop.preview_panel',
        'src.gui.desktop.table_editor',
        'src.gui.desktop.icon_manager',
        'src.converters.markdown_to_docx',
        'src.converters.formula_converter',
        'src.converters.latex_exporter',
        'src.converters.table_converter',
        'src.utils.config',
        'cairosvg',
        'PIL',
        'PIL._tkinter_finder',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Markdown2Academia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../assets/icon.ico' if os.path.exists('../../assets/icon.ico') else None,
)
