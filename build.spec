# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# 获取data目录下的所有文件
data_files = []
data_dir = 'data'
if os.path.exists(data_dir):
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            src = os.path.join(root, file)
            # 保持目录结构
            dst = root
            data_files.append((src, dst))

a = Analysis(
    ['adb_installer.py'],
    pathex=[],
    binaries=[],
    datas=data_files,  # 包含data目录下的所有文件
    hiddenimports=[],
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
    name='ADB_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,  # 需要管理员权限
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # 如果有图标文件
    version='version_info.txt' if os.path.exists('version_info.txt') else None,  # 版本信息
)