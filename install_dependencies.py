#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
依賴安裝腳本
自動安裝批量搜索所需的依賴
"""

import subprocess
import sys
import os


def install_package(package_name):
    """安裝Python包"""
    try:
        print(f"📦 正在安裝 {package_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", package_name], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package_name} 安裝成功")
            return True
        else:
            print(f"❌ {package_name} 安裝失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安裝 {package_name} 時發生錯誤: {str(e)}")
        return False


def install_playwright_browsers():
    """安裝Playwright瀏覽器"""
    try:
        print("🌐 正在安裝Playwright瀏覽器...")
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Playwright瀏覽器安裝成功")
            return True
        else:
            print(f"❌ Playwright瀏覽器安裝失敗: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 安裝Playwright瀏覽器時發生錯誤: {str(e)}")
        return False


def check_python_version():
    """檢查Python版本"""
    version = sys.version_info
    print(f"🐍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True


def main():
    """主函數"""
    print("🌟 批量公司搜索系統 - 依賴安裝")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 需要安裝的包
    required_packages = [
        "playwright",
        "beautifulsoup4",
        "asyncio",
        "requests"
    ]
    
    failed_packages = []
    
    # 安裝Python包
    for package in required_packages:
        if not install_package(package):
            failed_packages.append(package)
    
    # 安裝Playwright瀏覽器
    if "playwright" not in failed_packages:
        if not install_playwright_browsers():
            failed_packages.append("playwright-browsers")
    
    # 總結
    print("\n" + "=" * 50)
    if failed_packages:
        print("❌ 以下依賴安裝失敗:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n請手動安裝失敗的依賴:")
        for package in failed_packages:
            if package == "playwright-browsers":
                print("   playwright install chromium")
            else:
                print(f"   pip install {package}")
    else:
        print("🎉 所有依賴安裝成功!")
        print("您現在可以運行: python run_batch_search.py")
    
    print("=" * 50)


if __name__ == "__main__":
    main() 