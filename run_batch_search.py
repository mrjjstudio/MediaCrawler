#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量搜索啟動腳本
配置搜索參數並啟動批量搜索
"""

import asyncio
import os
import json
from datetime import datetime
from batch_company_search import BatchCompanySearch


class SearchConfig:
    """搜索配置類"""
    
    def __init__(self):
        self.config = {
            "batch_size": 50,  # 每批處理的公司數量
            "delay_between_searches": 5,  # 搜索間隔(秒)
            "max_wait_time": 60,  # 最大等待時間(秒)
            "auto_save_interval": 10,  # 自動保存間隔(每N個公司)
            "max_retries": 3,  # 最大重試次數
            "start_from_index": 0,  # 從第N個公司開始
            "enable_progress_report": True,  # 啟用進度報告
            "headless_mode": False,  # 無頭模式
            "concurrent_searches": 1,  # 並發搜索數量
        }
        
        self.load_config()
    
    def load_config(self):
        """載入配置文件"""
        if os.path.exists("search_config.json"):
            try:
                with open("search_config.json", 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                    print("📋 載入自定義配置")
            except Exception as e:
                print(f"⚠️ 載入配置失敗: {str(e)}")
        else:
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open("search_config.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("💾 配置已保存")
        except Exception as e:
            print(f"❌ 保存配置失敗: {str(e)}")
    
    def get(self, key, default=None):
        """獲取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """設置配置值"""
        self.config[key] = value
        self.save_config()
    
    def show_config(self):
        """顯示當前配置"""
        print("\n📋 當前搜索配置:")
        print("=" * 40)
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("=" * 40)


class BatchSearchManager:
    """批量搜索管理器"""
    
    def __init__(self):
        self.config = SearchConfig()
        self.searcher = None
    
    def check_prerequisites(self):
        """檢查前置條件"""
        print("🔍 檢查前置條件...")
        
        # 檢查公司列表文件
        if not os.path.exists("companylist2.md"):
            print("❌ 公司列表文件不存在: companylist2.md")
            return False
        
        # 檢查公司數量
        with open("companylist2.md", 'r', encoding='utf-8') as f:
            company_count = sum(1 for line in f if line.strip())
        
        print(f"📊 公司列表: {company_count} 家公司")
        
        # 檢查依賴
        try:
            import playwright
            from bs4 import BeautifulSoup
            print("✅ 所需依賴已安裝")
        except ImportError as e:
            print(f"❌ 缺少依賴: {str(e)}")
            print("請運行: pip install playwright beautifulsoup4")
            return False
        
        return True
    
    def estimate_time(self):
        """估算搜索時間"""
        try:
            with open("companylist2.md", 'r', encoding='utf-8') as f:
                total_companies = sum(1 for line in f if line.strip())
            
            # 載入已完成的進度
            completed = 0
            if os.path.exists("search_progress.json"):
                with open("search_progress.json", 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    completed = len(progress.get('processed_companies', []))
            
            remaining = total_companies - completed
            
            # 估算時間 (每個公司大約需要70秒)
            time_per_company = 70  # 60秒等待 + 10秒處理
            estimated_seconds = remaining * time_per_company
            
            hours = estimated_seconds // 3600
            minutes = (estimated_seconds % 3600) // 60
            
            print(f"\n⏱️  時間估算:")
            print(f"總公司數: {total_companies}")
            print(f"已完成: {completed}")
            print(f"剩餘: {remaining}")
            print(f"估算時間: {hours}小時 {minutes}分鐘")
            
            if hours > 8:
                print("⚠️  建議分批執行或調整搜索參數")
            
        except Exception as e:
            print(f"❌ 估算時間失敗: {str(e)}")
    
    def show_menu(self):
        """顯示選單"""
        print("\n🌟 批量公司聯絡資料搜索系統")
        print("=" * 50)
        print("1. 開始批量搜索")
        print("2. 查看搜索配置")
        print("3. 修改搜索配置")
        print("4. 查看搜索進度")
        print("5. 繼續未完成的搜索")
        print("6. 清除所有進度")
        print("7. 測試搜索功能")
        print("0. 退出")
        print("=" * 50)
    
    def modify_config(self):
        """修改配置"""
        print("\n🔧 修改搜索配置:")
        print("1. 搜索間隔時間")
        print("2. 自動保存間隔")
        print("3. 最大等待時間")
        print("4. 從指定位置開始")
        print("5. 恢復默認配置")
        
        choice = input("\n請選擇要修改的配置 (1-5): ").strip()
        
        try:
            if choice == "1":
                delay = int(input("請輸入搜索間隔時間(秒，建議5-10): "))
                self.config.set("delay_between_searches", delay)
                print("✅ 搜索間隔已更新")
            
            elif choice == "2":
                interval = int(input("請輸入自動保存間隔(每N個公司，建議5-20): "))
                self.config.set("auto_save_interval", interval)
                print("✅ 自動保存間隔已更新")
            
            elif choice == "3":
                wait_time = int(input("請輸入最大等待時間(秒，建議60-120): "))
                self.config.set("max_wait_time", wait_time)
                print("✅ 最大等待時間已更新")
            
            elif choice == "4":
                start_index = int(input("請輸入開始位置(公司編號，從0開始): "))
                self.config.set("start_from_index", start_index)
                print("✅ 開始位置已更新")
            
            elif choice == "5":
                self.config.config = SearchConfig().config
                self.config.save_config()
                print("✅ 配置已重置為默認值")
                
        except ValueError:
            print("❌ 輸入無效，請輸入數字")
    
    def view_progress(self):
        """查看搜索進度"""
        if not os.path.exists("search_progress.json"):
            print("⚠️ 沒有搜索進度記錄")
            return
        
        try:
            with open("search_progress.json", 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            processed = len(progress.get('processed_companies', []))
            results = len(progress.get('all_results', []))
            last_updated = progress.get('last_updated', 'Unknown')
            
            print("\n📊 搜索進度:")
            print(f"已處理公司: {processed}")
            print(f"成功獲取聯絡資料: {results}")
            print(f"成功率: {results/processed*100:.1f}%" if processed > 0 else "成功率: 0%")
            print(f"最後更新: {last_updated}")
            
        except Exception as e:
            print(f"❌ 查看進度失敗: {str(e)}")
    
    def clear_progress(self):
        """清除搜索進度"""
        confirm = input("⚠️ 確定要清除所有進度嗎？(y/N): ").strip().lower()
        
        if confirm == 'y':
            try:
                if os.path.exists("search_progress.json"):
                    os.remove("search_progress.json")
                print("✅ 搜索進度已清除")
            except Exception as e:
                print(f"❌ 清除進度失敗: {str(e)}")
        else:
            print("操作已取消")
    
    async def test_search(self):
        """測試搜索功能"""
        print("\n🧪 測試搜索功能...")
        
        # 讀取第一個公司名稱
        try:
            with open("companylist2.md", 'r', encoding='utf-8') as f:
                first_company = f.readline().strip()
            
            if not first_company:
                print("❌ 無法讀取測試公司")
                return
            
            print(f"測試公司: {first_company}")
            
            # 創建測試搜索實例
            test_searcher = BatchCompanySearch()
            
            # 設置瀏覽器
            await test_searcher.setup_browser()
            
            # 訪問百度AI
            if await test_searcher.access_baidu_ai():
                print("✅ 成功訪問百度AI")
                
                # 測試搜索
                result = await test_searcher.search_single_company(first_company)
                
                if result:
                    print("✅ 測試搜索成功")
                    print(f"公司名稱: {result.get('company_name')}")
                    print(f"電話: {result.get('phone')}")
                    print(f"郵箱: {result.get('email')}")
                    print(f"地址: {result.get('address')}")
                else:
                    print("❌ 測試搜索失敗")
            else:
                print("❌ 無法訪問百度AI")
            
            # 清理資源
            await test_searcher.cleanup()
            
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
    
    async def run_batch_search(self, resume=False):
        """運行批量搜索"""
        if not self.check_prerequisites():
            return
        
        self.estimate_time()
        
        if not resume:
            confirm = input("\n🚀 確定要開始批量搜索嗎？(y/N): ").strip().lower()
            if confirm != 'y':
                print("操作已取消")
                return
        
        print("\n開始批量搜索...")
        
        # 創建搜索實例
        searcher = BatchCompanySearch()
        
        # 應用配置
        searcher.batch_delay = self.config.get("delay_between_searches", 5)
        searcher.max_retries = self.config.get("max_retries", 3)
        
        # 開始搜索
        await searcher.run_batch_search()
    
    async def main_menu(self):
        """主選單"""
        while True:
            self.show_menu()
            choice = input("\n請選擇操作 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再見!")
                break
            
            elif choice == "1":
                await self.run_batch_search()
            
            elif choice == "2":
                self.config.show_config()
            
            elif choice == "3":
                self.modify_config()
            
            elif choice == "4":
                self.view_progress()
            
            elif choice == "5":
                await self.run_batch_search(resume=True)
            
            elif choice == "6":
                self.clear_progress()
            
            elif choice == "7":
                await self.test_search()
            
            else:
                print("❌ 無效選擇，請重新輸入")
            
            input("\n按任意鍵繼續...")


async def main():
    """主函數"""
    manager = BatchSearchManager()
    await manager.main_menu()


if __name__ == "__main__":
    asyncio.run(main()) 