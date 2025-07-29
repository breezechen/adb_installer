#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyInstaller打包脚本
"""

import os
import subprocess
import shutil

def build():
    """执行打包"""
    print("开始打包ADB安装器...")
    
    # 检查必要文件
    if not os.path.exists('adb_installer.py'):
        print("错误：找不到主程序文件 adb_installer.py")
        return
    
    if not os.path.exists('data'):
        print("错误：找不到data目录")
        return
    
    # 检查data目录下的必要文件
    required_files = [
        'data/platform-tools-latest-windows.zip',
        'data/usb_driver_r13-windows.zip'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误：找不到必要文件 {file}")
            return
    
    # 清理之前的构建
    for dir in ['build', 'dist']:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    
    # 执行打包
    try:
        subprocess.run([
            'pyinstaller',
            'build.spec',
            '--clean'
        ], check=True)
        
        print("\n打包成功！")
        print("可执行文件位于: dist/ADB_Installer.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败: {e}")
    except FileNotFoundError:
        print("错误：未找到pyinstaller，请先安装: pip install pyinstaller")

if __name__ == "__main__":
    build()