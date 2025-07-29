# ADB for Windows Installer

Windows系统下的ADB（Android Debug Bridge）安装器，提供图形界面的一键安装/卸载功能。

## 功能特性

- ✅ 图形化安装界面
- ✅ 自动配置环境变量
- ✅ USB驱动自动安装
- ✅ 注册表记录安装信息
- ✅ 一键卸载功能
- ✅ 管理员权限自动提升

## 使用方法

### 安装ADB

1. 双击运行 `ADB_Installer.exe`
2. 程序会自动请求管理员权限
3. 选择安装目录（默认为 `%APPDATA%\ADB`）
4. 点击"安装"按钮
5. 等待安装完成

### 卸载ADB

1. 双击运行 `ADB_Installer.exe`
2. 如果已安装，会显示"卸载"按钮
3. 点击"卸载"按钮确认卸载

## 开发说明

### 环境要求

- Python 3.8+
- Windows 10/11
- 管理员权限

### 依赖安装

```bash
pip install -r requirements.txt
```

### 打包说明

1. 确保 `data` 目录下包含以下文件：
   - `platform-tools-latest-windows.zip`
   - `usb_driver_r13-windows.zip`

2. 运行打包脚本：

```bash
python build.py
```

3. 打包完成后，可执行文件位于 `dist/ADB_Installer.exe`

## 技术细节

- 使用 tkinter 构建GUI界面
- 通过注册表 `HKLM\SOFTWARE\ADBInstaller` 记录安装信息
- 环境变量配置到系统PATH（优先级最高）
- 使用 pnputil 安装USB驱动
- PyInstaller 打包为单文件可执行程序

## 注意事项

- 需要管理员权限才能修改系统环境变量和注册表
- 如果系统已存在其他Android驱动，将跳过驱动安装
- 卸载时仅移除ADB工具，不会卸载USB驱动
- 环境变量更改后需要重新打开命令提示符才能生效