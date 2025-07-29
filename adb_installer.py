#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ADB for Windows Installer
Windows系统下的ADB安装器
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import winreg
import zipfile
import shutil
import ctypes
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('adb_installer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 常量定义
REGISTRY_PATH = r"SOFTWARE\ADBInstaller"
REGISTRY_KEY = "InstallPath"
DEFAULT_INSTALL_PATH = os.path.join(os.environ['APPDATA'], 'ADB')
PLATFORM_TOOLS_ZIP = "platform-tools-latest-windows.zip"
USB_DRIVER_ZIP = "usb_driver_r13-windows.zip"

class ADBInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ADB 安装器")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass
        
        self.install_path = DEFAULT_INSTALL_PATH
        self.is_installed = False
        self.installed_path = None
        
        # 检查是否需要管理员权限
        if not self.is_admin():
            self.request_admin()
            sys.exit(0)
        
        # 初始化UI
        self.init_ui()
        
        # 检查安装状态
        self.check_installation_status()
    
    def is_admin(self):
        """检查是否具有管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def request_admin(self):
        """请求管理员权限"""
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            " ".join(sys.argv),
            None,
            1
        )
    
    def init_ui(self):
        """初始化用户界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="ADB for Windows 安装器",
            font=("Microsoft YaHei", 16, "bold")
        )
        title_label.pack(pady=20)
        
        # 状态标签
        self.status_label = tk.Label(
            self.root,
            text="正在检查安装状态...",
            font=("Microsoft YaHei", 10)
        )
        self.status_label.pack(pady=10)
        
        # 路径框架
        self.path_frame = tk.Frame(self.root)
        self.path_frame.pack(pady=10)
        
        self.path_label = tk.Label(
            self.path_frame,
            text="安装路径:",
            font=("Microsoft YaHei", 10)
        )
        self.path_label.grid(row=0, column=0, padx=5)
        
        self.path_entry = tk.Entry(
            self.path_frame,
            width=40,
            font=("Microsoft YaHei", 10)
        )
        self.path_entry.insert(0, self.install_path)
        self.path_entry.grid(row=0, column=1, padx=5)
        
        self.browse_button = tk.Button(
            self.path_frame,
            text="浏览",
            command=self.browse_folder,
            font=("Microsoft YaHei", 10)
        )
        self.browse_button.grid(row=0, column=2, padx=5)
        
        # 进度条
        self.progress_frame = tk.Frame(self.root)
        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=("Microsoft YaHei", 9)
        )
        self.progress_label.pack()
        
        # 操作按钮
        self.action_button = tk.Button(
            self.root,
            text="安装",
            command=self.perform_action,
            font=("Microsoft YaHei", 12),
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white"
        )
        self.action_button.pack(pady=20)
        
        # 版权信息
        copyright_label = tk.Label(
            self.root,
            text="© 2024 ADB Installer",
            font=("Microsoft YaHei", 8),
            fg="gray"
        )
        copyright_label.pack(side=tk.BOTTOM, pady=5)
    
    def browse_folder(self):
        """浏览文件夹"""
        folder = filedialog.askdirectory(
            title="选择安装目录",
            initialdir=os.path.dirname(self.install_path)
        )
        if folder:
            self.install_path = os.path.join(folder, 'ADB')
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, self.install_path)
    
    def check_installation_status(self):
        """检查ADB安装状态"""
        try:
            # 从注册表读取安装信息
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH) as key:
                installed_path = winreg.QueryValueEx(key, REGISTRY_KEY)[0]
                if os.path.exists(installed_path) and os.path.exists(os.path.join(installed_path, "platform-tools", "adb.exe")):
                    self.is_installed = True
                    self.installed_path = installed_path
                    self.update_ui_for_uninstall()
                else:
                    # 注册表存在但文件不存在，清理注册表
                    self.clean_registry()
                    self.update_ui_for_install()
        except WindowsError:
            # 注册表不存在
            self.update_ui_for_install()
    
    def update_ui_for_install(self):
        """更新UI为安装模式"""
        self.status_label.config(text="系统未安装ADB，请选择安装路径")
        self.path_frame.pack()
        self.progress_frame.pack_forget()
        self.action_button.config(text="安装", bg="#4CAF50", command=self.install_adb)
    
    def update_ui_for_uninstall(self):
        """更新UI为卸载模式"""
        self.status_label.config(text=f"ADB已安装在: {self.installed_path}")
        self.path_frame.pack_forget()
        self.progress_frame.pack_forget()
        self.action_button.config(text="卸载", bg="#f44336", command=self.uninstall_adb)
    
    def show_progress(self, message):
        """显示进度信息"""
        self.progress_frame.pack(pady=10)
        self.progress_label.config(text=message)
        self.root.update()
    
    def perform_action(self):
        """执行安装或卸载操作"""
        if self.is_installed:
            self.uninstall_adb()
        else:
            self.install_adb()
    
    def install_adb(self):
        """安装ADB"""
        self.action_button.config(state=tk.DISABLED)
        
        # 在新线程中执行安装
        thread = threading.Thread(target=self._install_process)
        thread.start()
    
    def _install_process(self):
        """安装过程"""
        try:
            # 获取安装路径
            install_path = self.path_entry.get()
            
            # 检查现有ADB
            self.show_progress("正在检查系统中的ADB...")
            if self.check_existing_adb():
                response = messagebox.askyesno(
                    "ADB已存在",
                    "系统环境变量中已存在adb命令，是否继续安装？\n如果继续，新版本将被设置为优先使用。"
                )
                if not response:
                    self.show_progress("安装已取消")
                    self.action_button.config(state=tk.NORMAL)
                    return
            
            # 创建安装目录
            self.show_progress("正在创建安装目录...")
            os.makedirs(install_path, exist_ok=True)
            
            # 解压platform-tools
            self.show_progress("正在解压ADB工具...")
            self.extract_platform_tools(install_path)
            
            # 解压USB驱动
            self.show_progress("正在解压USB驱动...")
            self.extract_usb_driver(install_path)
            
            # 添加到环境变量
            self.show_progress("正在配置环境变量...")
            self.add_to_path(os.path.join(install_path, "platform-tools"))
            
            # 检查并安装驱动
            self.show_progress("正在检查USB驱动...")
            if not self.check_android_driver():
                self.show_progress("正在安装USB驱动...")
                self.install_driver(install_path)
            else:
                self.show_progress("系统已存在Android驱动，跳过驱动安装")
            
            # 写入注册表
            self.show_progress("正在写入注册表...")
            self.write_registry(install_path)
            
            # 完成
            self.show_progress("安装完成！")
            messagebox.showinfo("安装成功", "ADB已成功安装！\n请重新打开命令提示符以使用adb命令。")
            
            # 更新UI
            self.is_installed = True
            self.installed_path = install_path
            self.root.after(0, self.update_ui_for_uninstall)
            
        except Exception as e:
            logging.error(f"安装失败: {str(e)}")
            messagebox.showerror("安装失败", f"安装过程中出现错误:\n{str(e)}")
        finally:
            self.action_button.config(state=tk.NORMAL)
    
    def uninstall_adb(self):
        """卸载ADB"""
        response = messagebox.askyesno("确认卸载", "确定要卸载ADB吗？")
        if not response:
            return
        
        self.action_button.config(state=tk.DISABLED)
        
        # 在新线程中执行卸载
        thread = threading.Thread(target=self._uninstall_process)
        thread.start()
    
    def _uninstall_process(self):
        """卸载过程"""
        try:
            # 从环境变量移除
            self.show_progress("正在清理环境变量...")
            self.remove_from_path(os.path.join(self.installed_path, "platform-tools"))
            
            # 删除文件
            self.show_progress("正在删除文件...")
            if os.path.exists(self.installed_path):
                shutil.rmtree(self.installed_path)
            
            # 清理注册表
            self.show_progress("正在清理注册表...")
            self.clean_registry()
            
            # 完成
            self.show_progress("卸载完成！")
            messagebox.showinfo("卸载成功", "ADB已成功卸载！")
            
            # 更新UI
            self.is_installed = False
            self.installed_path = None
            self.root.after(0, self.update_ui_for_install)
            
        except Exception as e:
            logging.error(f"卸载失败: {str(e)}")
            messagebox.showerror("卸载失败", f"卸载过程中出现错误:\n{str(e)}")
        finally:
            self.action_button.config(state=tk.NORMAL)
    
    def check_existing_adb(self):
        """检查系统中是否已存在adb"""
        try:
            result = subprocess.run(['where', 'adb'], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def extract_platform_tools(self, install_path):
        """解压platform-tools"""
        zip_path = self.get_resource_path(os.path.join("data", PLATFORM_TOOLS_ZIP))
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
    
    def extract_usb_driver(self, install_path):
        """解压USB驱动"""
        zip_path = self.get_resource_path(os.path.join("data", USB_DRIVER_ZIP))
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(install_path)
    
    def check_android_driver(self):
        """检查是否已安装Android驱动"""
        try:
            # 检查设备管理器中是否有Android设备类
            result = subprocess.run(
                ['wmic', 'path', 'Win32_PnPEntity', 'where', 
                 'Name like "%Android%"', 'get', 'Name'],
                capture_output=True,
                text=True
            )
            return 'Android' in result.stdout
        except:
            return False
    
    def install_driver(self, install_path):
        """安装USB驱动"""
        inf_path = os.path.join(install_path, "usb_driver", "android_winusb.inf")
        try:
            # 使用pnputil安装驱动
            result = subprocess.run(
                ['pnputil', '/a', inf_path],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logging.warning(f"驱动安装可能失败: {result.stderr}")
        except Exception as e:
            logging.error(f"驱动安装失败: {str(e)}")
    
    def add_to_path(self, path):
        """添加到系统PATH环境变量（放在最前面）"""
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            ) as key:
                current_path = winreg.QueryValueEx(key, "Path")[0]
                
                # 移除已存在的相同路径
                path_list = [p for p in current_path.split(';') if p.strip() and p.strip() != path]
                
                # 将新路径添加到最前面
                new_path = path + ';' + ';'.join(path_list)
                
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                
                # 广播环境变量更改
                self.broadcast_environment_change()
        except Exception as e:
            logging.error(f"添加PATH失败: {str(e)}")
            raise
    
    def remove_from_path(self, path):
        """从系统PATH环境变量移除"""
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            ) as key:
                current_path = winreg.QueryValueEx(key, "Path")[0]
                
                # 移除指定路径
                path_list = [p for p in current_path.split(';') if p.strip() and p.strip() != path]
                new_path = ';'.join(path_list)
                
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                
                # 广播环境变量更改
                self.broadcast_environment_change()
        except Exception as e:
            logging.error(f"移除PATH失败: {str(e)}")
            raise
    
    def broadcast_environment_change(self):
        """广播环境变量更改消息"""
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 0x0002
        
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            5000,
            None
        )
    
    def write_registry(self, install_path):
        """写入注册表"""
        try:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH) as key:
                winreg.SetValueEx(key, REGISTRY_KEY, 0, winreg.REG_SZ, install_path)
        except Exception as e:
            logging.error(f"写入注册表失败: {str(e)}")
            raise
    
    def clean_registry(self):
        """清理注册表"""
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH)
        except:
            pass
    
    def get_resource_path(self, relative_path):
        """获取资源文件路径（支持PyInstaller打包）"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ADBInstaller()
    app.run()