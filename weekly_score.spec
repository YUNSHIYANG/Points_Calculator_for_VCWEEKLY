# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller打包配置文件

用于将周刊得点计算器打包为可执行文件。
"""

import sys
import os
from pathlib import Path

block_cipher = None

# 项目根目录
project_root = Path(SPECPATH)

# 查找 Python DLL
python_dll = None
python_dir = Path(sys.executable).parent
for dll in python_dir.glob('python*.dll'):
    python_dll = str(dll)
    break

# 收集数据文件
datas = [
    (str(project_root / 'config'), 'config'),
    (str(project_root / 'resources'), 'resources'),
]

# 收集二进制文件（包括 Python DLL）
binaries = []
if python_dll:
    binaries.append((python_dll, '.'))

# 收集隐式导入
hiddenimports = [
    'PyQt6',
    'PyQt6.QtWidgets',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.sip',
    'requests',
    'aiohttp',
    'openpyxl',
    'pydantic',
    'loguru',
    'tomli_w',
    'weekly_score',
    'weekly_score.core',
    'weekly_score.core.api',
    'weekly_score.core.calculator',
    'weekly_score.core.excel_io',
    'weekly_score.core.models',
    'weekly_score.gui',
    'weekly_score.gui.main_window',
    'weekly_score.gui.widgets',
    'weekly_score.gui.widgets.fluent_card',
    'weekly_score.gui.widgets.score_display',
    'weekly_score.gui.widgets.input_field',
    'weekly_score.gui.dialogs',
    'weekly_score.gui.dialogs.settings_dialog',
    'weekly_score.gui.styles',
    'weekly_score.gui.styles.fluent_theme',
    'weekly_score.utils',
    'weekly_score.utils.config',
    'weekly_score.utils.logger',
    'weekly_score.utils.validators',
]

a = Analysis(
    ['run.py'],
    pathex=[str(project_root), str(project_root / 'src')],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='周刊得点计算器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'resources' / 'icons' / 'app.ico') if (project_root / 'resources' / 'icons' / 'app.ico').exists() else None,
)