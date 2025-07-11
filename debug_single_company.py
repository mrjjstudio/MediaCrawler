#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
詳細調試單個公司搜索腳本
用於診斷數據提取問題
"""

import asyncio
import csv
import os
from datetime import datetime
from batch_company_search import BatchCompanySearch


class DebugSingleCompany:
    """調試單個公司搜索"""
    
    def __init__(self, company_name: str):
        self.company_name = company_name
        self.searcher = None
    
    async def debug_search(self):
        """調試搜索過程"""
        print(f"🔍 開始調試搜索: {self.company_name}")
        print("=" * 60)
        
        # 創建搜索實例
        self.searcher = BatchCompanySearch()
        
        try:
            # 設置瀏覽器
            await self.searcher.setup_browser()
            
            # 訪問百度AI
            if not await self.searcher.access_baidu_ai():
                print("❌ 無法訪問百度AI")
                return
            
            # 調試不同的搜索查詢
            search_queries = [
                f"{self.company_name} 聯絡資料",
                f"{self.company_name} 電話 郵箱",
                f"{self.company_name} 聯繫方式",
                f"{self.company_name} 公司信息",
                f"{self.company_name} 企業信息"
            ]
            
            for i, query in enumerate(search_queries, 1):
                print(f"\n🔍 測試查詢 {i}: {query}")
                print("-" * 40)
                
                # 執行搜索
                await self.search_with_query(query)
                
                # 等待一段時間再嘗試下一個查詢
                if i < len(search_queries):
                    print("⏳ 等待5秒後嘗試下一個查詢...")
                    await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ 調試過程中發生錯誤: {str(e)}")
        
        finally:
            # 清理資源
            if self.searcher:
                await self.searcher.cleanup()
    
    async def search_with_query(self, query: str):
        """使用特定查詢搜索"""
        try:
            # 刷新頁面
            await self.searcher.page.reload(wait_until='networkidle')
            await self.searcher.page.wait_for_timeout(2000)
            
            # 查找輸入框
            input_selectors = [
                '[contenteditable="true"]',
                'textarea[placeholder*="输入"]',
                'input[type="text"]'
            ]
            
            input_box = None
            for selector in input_selectors:
                try:
                    element = await self.searcher.page.query_selector(selector)
                    if element and await element.is_visible():
                        input_box = element
                        break
                except:
                    continue
            
            if not input_box:
                print("❌ 未找到輸入框")
                return
            
            # 輸入搜索查詢
            await input_box.click()
            await input_box.fill("")
            await input_box.type(query)
            await self.searcher.page.keyboard.press('Enter')
            
            # 等待AI回復
            await self.searcher.page.wait_for_timeout(5000)
            
            # 等待回復完成
            max_wait_time = 30
            wait_interval = 2
            waited_time = 0
            
            while waited_time < max_wait_time:
                page_text = await self.searcher.page.text_content('body')
                
                if "请等待" not in page_text and "回答中" not in page_text:
                    break
                
                await self.searcher.page.wait_for_timeout(wait_interval * 1000)
                waited_time += wait_interval
            
            # 分析回答內容
            await self.analyze_response()
            
        except Exception as e:
            print(f"❌ 搜索失敗: {str(e)}")
    
    async def analyze_response(self):
        """分析AI回答內容"""
        try:
            # 獲取最新AI回答
            latest_response = await self.searcher.get_latest_ai_response()
            
            if latest_response:
                print(f"✅ 找到AI回答 (長度: {len(latest_response)})")
                print(f"📝 AI回答內容:")
                print("-" * 30)
                print(latest_response[:500] + "..." if len(latest_response) > 500 else latest_response)
                print("-" * 30)
            else:
                print("❌ 未找到AI回答，使用整個頁面")
                
                # 獲取整個頁面文本
                page_text = await self.searcher.page.text_content('body')
                print(f"📄 頁面文本長度: {len(page_text)}")
                print(f"📝 頁面文本片段:")
                print("-" * 30)
                print(page_text[:500] + "..." if len(page_text) > 500 else page_text[:500])
                print("-" * 30)
                
                latest_response = page_text
            
            # 提取相關文本
            relevant_text = self.searcher.extract_relevant_text(latest_response, self.company_name)
            print(f"🎯 相關文本長度: {len(relevant_text)}")
            print(f"📝 相關文本:")
            print("-" * 30)
            print(relevant_text[:300] + "..." if len(relevant_text) > 300 else relevant_text)
            print("-" * 30)
            
            # 測試數據提取
            print("🔍 數據提取測試:")
            phone = self.searcher.extract_phone(relevant_text)
            emails = self.searcher.extract_emails(relevant_text)
            address = self.searcher.extract_address(relevant_text)
            legal_rep = self.searcher.extract_legal_representative(relevant_text)
            
            print(f"📞 電話: '{phone}'")
            print(f"📧 郵箱: {emails}")
            print(f"📍 地址: '{address}'")
            print(f"👤 法人: '{legal_rep}'")
            
        except Exception as e:
            print(f"❌ 分析回答失敗: {str(e)}")
    
    async def save_debug_info(self, content: str, filename: str):
        """保存調試信息"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_filename = f"debug_{filename}_{timestamp}.txt"
            
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 調試信息已保存到: {debug_filename}")
            
        except Exception as e:
            print(f"❌ 保存調試信息失敗: {str(e)}")


async def main():
    """主函數"""
    print("🧪 單個公司搜索調試工具")
    print("=" * 50)
    
    # 從公司列表中選擇一家進行調試
    try:
        with open("companylist2.md", 'r', encoding='utf-8') as f:
            companies = []
            for line in f:
                company = line.strip()
                if company and not company.startswith('#'):
                    companies.append(company)
                    if len(companies) >= 10:  # 只顯示前10家
                        break
        
        print("請選擇要調試的公司:")
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company}")
        
        choice = input(f"\n請輸入編號 (1-{len(companies)}): ").strip()
        
        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(companies):
                selected_company = companies[choice_idx]
                
                print(f"\n🎯 選擇的公司: {selected_company}")
                
                # 開始調試
                debugger = DebugSingleCompany(selected_company)
                await debugger.debug_search()
                
            else:
                print("❌ 無效的選擇")
        except ValueError:
            print("❌ 請輸入有效的數字")
    
    except FileNotFoundError:
        print("❌ 公司列表文件不存在")


if __name__ == "__main__":
    asyncio.run(main()) 