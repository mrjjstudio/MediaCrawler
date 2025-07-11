#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量公司聯絡資料搜索腳本
處理大量公司並獲取聯絡資料
"""

import asyncio
import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import re


class BatchCompanySearch:
    """批量公司搜索類"""
    
    def __init__(self, company_list_file: str = "companylist2.md"):
        self.company_list_file = company_list_file
        self.search_url = "https://chat.baidu.com/search?extParams=%7B%22enter_type%22%3A%22ai_explore_home%22%7D&isShowHello=1"
        self.playwright = None
        self.browser = None
        self.page = None
        
        # 批量處理設置
        self.batch_delay = 5  # 每次搜索後等待5秒
        self.max_retries = 3  # 最大重試次數
        self.results_dir = "batch_results"
        self.progress_file = "search_progress.json"
        
        # 創建結果目錄
        os.makedirs(self.results_dir, exist_ok=True)
        
        # 結果存儲
        self.all_results = []
        self.processed_companies = set()
        
        # 載入之前的進度
        self.load_progress()
    
    def load_progress(self):
        """載入之前的搜索進度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    self.processed_companies = set(progress_data.get('processed_companies', []))
                    self.all_results = progress_data.get('all_results', [])
                    print(f"📊 載入之前的進度: 已處理 {len(self.processed_companies)} 家公司")
            except Exception as e:
                print(f"⚠️ 載入進度文件失敗: {str(e)}")
        else:
            print("🆕 開始全新的批量搜索")
    
    def save_progress(self):
        """保存搜索進度"""
        try:
            progress_data = {
                'processed_companies': list(self.processed_companies),
                'all_results': self.all_results,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
            print(f"💾 進度已保存: {len(self.processed_companies)} 家公司")
        except Exception as e:
            print(f"❌ 保存進度失敗: {str(e)}")
    
    def load_company_list(self) -> List[str]:
        """載入公司列表"""
        companies = []
        
        try:
            with open(self.company_list_file, 'r', encoding='utf-8') as f:
                for line in f:
                    company = line.strip()
                    if company and not company.startswith('#'):  # 跳過空行和註釋
                        companies.append(company)
            
            print(f"📋 載入公司列表: {len(companies)} 家公司")
            
            # 過濾掉已處理的公司
            remaining_companies = [c for c in companies if c not in self.processed_companies]
            print(f"📋 剩餘待處理: {len(remaining_companies)} 家公司")
            
            return remaining_companies
            
        except FileNotFoundError:
            print(f"❌ 公司列表文件不存在: {self.company_list_file}")
            return []
        except Exception as e:
            print(f"❌ 載入公司列表失敗: {str(e)}")
            return []
    
    async def setup_browser(self):
        """設置瀏覽器"""
        print("🚀 啟動瀏覽器...")
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # 顯示瀏覽器以便監控
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
        
        # 隱藏自動化特徵
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        print("✅ 瀏覽器設置完成")
    
    async def access_baidu_ai(self):
        """訪問百度AI"""
        print("🌐 訪問百度AI搜索...")
        
        try:
            await self.page.goto(self.search_url, wait_until='networkidle', timeout=30000)
            await self.page.wait_for_timeout(3000)
            
            title = await self.page.title()
            print(f"📄 頁面標題: {title}")
            
            if "百度" in title:
                print("✅ 成功訪問百度AI搜索")
                return True
            else:
                print("❌ 未能正確訪問百度AI搜索")
                return False
        except Exception as e:
            print(f"❌ 訪問失敗: {str(e)}")
            return False
    
    async def search_single_company(self, company_name: str) -> Optional[Dict]:
        """搜索單個公司的聯絡資料"""
        print(f"\n🔍 搜索公司: {company_name}")
        
        try:
            # 刷新頁面以清除之前的搜索結果
            await self.page.reload(wait_until='networkidle')
            await self.page.wait_for_timeout(2000)
            
            # 發送搜索查詢
            search_query = f"{company_name} 聯絡資料"
            
            # 查找輸入框
            input_selectors = [
                '[contenteditable="true"]',
                'textarea[placeholder*="输入"]',
                'input[type="text"]'
            ]
            
            input_box = None
            for selector in input_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        input_box = element
                        break
                except:
                    continue
            
            if not input_box:
                print("❌ 未找到輸入框")
                return None
            
            # 輸入搜索查詢
            await input_box.click()
            await input_box.fill("")
            await input_box.type(search_query)
            await self.page.keyboard.press('Enter')
            
            # 等待AI回復
            await self.page.wait_for_timeout(5000)
            
            # 智能等待AI完成回復
            max_wait_time = 60
            wait_interval = 3
            waited_time = 0
            
            while waited_time < max_wait_time:
                page_text = await self.page.text_content('body')
                
                if "请等待" not in page_text and "回答中" not in page_text:
                    if self.has_contact_info(page_text):
                        print("✅ AI回復完成，找到聯絡資料！")
                        break
                
                await self.page.wait_for_timeout(wait_interval * 1000)
                waited_time += wait_interval
            
            # 提取聯絡資料
            contact_info = await self.extract_contact_info(company_name)
            
            if contact_info:
                print(f"✅ 成功獲取 {company_name} 的聯絡資料")
                return contact_info
            else:
                print(f"❌ 未能獲取 {company_name} 的聯絡資料")
                return None
                
        except Exception as e:
            print(f"❌ 搜索 {company_name} 失敗: {str(e)}")
            return None
    
    def has_contact_info(self, page_text: str) -> bool:
        """檢查是否包含聯絡資料"""
        contact_keywords = [
            "电话", "電話", "聯絡", "联系", "邮箱", "郵箱", "地址", 
            "法定代表人", "注册资本", "成立", "021-", "@", "有限公司"
        ]
        
        keyword_count = sum(1 for keyword in contact_keywords if keyword in page_text)
        return keyword_count >= 5 or len(page_text) > 3000
    
    async def get_latest_ai_response(self) -> Optional[str]:
        """獲取最新的AI回答內容"""
        try:
            # 嘗試不同的選擇器來找到AI回答區域
            ai_response_selectors = [
                '[data-testid="chat-answer"]',
                '.chat-answer',
                '.answer-content',
                '[class*="answer"]',
                '[class*="response"]',
                '[class*="chat-content"]'
            ]
            
            for selector in ai_response_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        # 取最後一個元素（最新的回答）
                        latest_element = elements[-1]
                        response_text = await latest_element.text_content()
                        if response_text and len(response_text) > 100:
                            return response_text.strip()
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ 獲取最新AI回答失敗: {str(e)}")
            return None
    
    def extract_relevant_text(self, page_text: str, company_name: str) -> str:
        """提取與當前公司相關的文本段落"""
        try:
            # 分割文本為段落
            paragraphs = page_text.split('\n')
            relevant_paragraphs = []
            
            # 提取公司名稱中的關鍵詞
            company_keywords = []
            if '有限公司' in company_name:
                company_keywords.append(company_name.replace('有限公司', ''))
            if '股份有限公司' in company_name:
                company_keywords.append(company_name.replace('股份有限公司', ''))
            
            # 添加完整公司名稱
            company_keywords.append(company_name)
            
            # 查找包含公司名稱或關鍵詞的段落
            for paragraph in paragraphs:
                if len(paragraph.strip()) < 10:
                    continue
                    
                # 檢查是否包含公司相關信息
                for keyword in company_keywords:
                    if keyword in paragraph:
                        relevant_paragraphs.append(paragraph)
                        break
                else:
                    # 如果段落包含聯絡資料關鍵詞，也包含
                    contact_keywords = ["电话", "電話", "邮箱", "郵箱", "地址", "法定代表人", "注册资本"]
                    if any(kw in paragraph for kw in contact_keywords):
                        relevant_paragraphs.append(paragraph)
            
            # 如果沒有找到相關段落，返回最近的一些段落
            if not relevant_paragraphs:
                print(f"⚠️ 未找到 {company_name} 的相關段落，使用最近的內容")
                # 取最後的幾個有內容的段落
                non_empty_paragraphs = [p for p in paragraphs if len(p.strip()) > 20]
                relevant_paragraphs = non_empty_paragraphs[-5:] if len(non_empty_paragraphs) > 5 else non_empty_paragraphs
            
            relevant_text = '\n'.join(relevant_paragraphs)
            print(f"📄 提取相關文本長度: {len(relevant_text)}")
            
            return relevant_text
            
        except Exception as e:
            print(f"⚠️ 提取相關文本失敗: {str(e)}")
            return page_text[:2000]  # 返回前2000字符作為後備
    
    async def extract_contact_info(self, company_name: str) -> Optional[Dict]:
        """提取聯絡資料"""
        try:
            # 等待頁面穩定
            await self.page.wait_for_timeout(2000)
            
            # 嘗試找到最新的AI回答區域
            latest_response = await self.get_latest_ai_response()
            
            if latest_response:
                # 從最新回答中提取信息
                page_text = latest_response
                print(f"🔍 使用最新AI回答提取數據 (長度: {len(page_text)})")
            else:
                # 如果無法找到最新回答，使用整個頁面
                html_content = await self.page.content()
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # 移除腳本和樣式
                for script in soup(["script", "style"]):
                    script.decompose()
                
                page_text = soup.get_text()
                print(f"⚠️ 使用整個頁面提取數據 (長度: {len(page_text)})")
            
            # 只提取包含公司名稱的相關段落
            relevant_text = self.extract_relevant_text(page_text, company_name)
            
            # 使用正則表達式提取聯絡資料
            contact_info = {
                'company_name': company_name,
                'phone': self.extract_phone(relevant_text),
                'email': self.extract_emails(relevant_text),
                'address': self.extract_address(relevant_text),
                'legal_representative': self.extract_legal_representative(relevant_text),
                'registered_capital': self.extract_registered_capital(relevant_text),
                'established_date': self.extract_established_date(relevant_text),
                'business_scope': self.extract_business_scope(relevant_text),
                'raw_text': relevant_text[:1000]  # 保留前1000字符作為原始數據
            }
            
            return contact_info
            
        except Exception as e:
            print(f"❌ 提取聯絡資料失敗: {str(e)}")
            return None
    
    def extract_phone(self, text: str) -> str:
        """提取電話號碼"""
        phone_patterns = [
            r'(?:电话|電話|聯絡電話|联系电话|Tel|TEL)[:：]?\s*([0-9\-\+\s\(\)]{8,20})',
            r'(\d{3,4}[-\s]?\d{7,8})',
            r'(\+86[-\s]?\d{3,4}[-\s]?\d{7,8})',
            r'(021[-\s]?\d{8})',
            r'(400[-\s]?\d{3}[-\s]?\d{4})'
        ]
        
        for pattern in phone_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_emails(self, text: str) -> List[str]:
        """提取多個郵箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # 去除重複並過濾無效郵箱
        unique_emails = []
        for email in emails:
            if email not in unique_emails and '@' in email and '.' in email:
                unique_emails.append(email)
        
        return unique_emails
    
    def extract_address(self, text: str) -> str:
        """提取地址"""
        address_patterns = [
            r'(?:地址|地址|Address|住址)[:：]?\s*([^。\n\r]{10,100})',
            r'(上海市[^。\n\r]{5,80})',
            r'(北京市[^。\n\r]{5,80})',
            r'(广州市[^。\n\r]{5,80})',
            r'(深圳市[^。\n\r]{5,80})',
            r'([^。\n\r]*区[^。\n\r]*路[^。\n\r]*号[^。\n\r]*)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_legal_representative(self, text: str) -> str:
        """提取法定代表人"""
        patterns = [
            r'(?:法定代表人|法人代表|负责人)[:：]?\s*([^。\n\r]{2,10})',
            r'法定代表人\s*([^。\n\r]{2,10})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_registered_capital(self, text: str) -> str:
        """提取注册资本"""
        patterns = [
            r'(?:注册资本|注冊資本|资本)[:：]?\s*([0-9,，.万亿元]+)',
            r'资本\s*([0-9,，.万亿元]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_established_date(self, text: str) -> str:
        """提取成立日期"""
        patterns = [
            r'(?:成立时间|成立日期|注册时间|注册日期)[:：]?\s*([0-9\-/年月日]{8,20})',
            r'成立于\s*([0-9\-/年月日]{8,20})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_business_scope(self, text: str) -> str:
        """提取經營範圍"""
        patterns = [
            r'(?:经营范围|經營範圍|业务范围|主营业务)[:：]?\s*([^。\n\r]{20,200})',
            r'经营范围\s*([^。\n\r]{20,200})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def save_results_to_csv(self, filename: str = None):
        """保存結果到CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"batch_company_contacts_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if not self.all_results:
                    print("⚠️ 沒有結果可保存")
                    return
                
                fieldnames = [
                    'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'registered_capital', 
                    'established_date', 'business_scope'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.all_results:
                    # 處理多個郵箱
                    email_list = result.get('email', [])
                    if isinstance(email_list, list):
                        email_str = '; '.join(email_list)
                    else:
                        email_str = email_list
                    
                    # 寫入行
                    row = {
                        'company_name': result.get('company_name', ''),
                        'phone': result.get('phone', ''),
                        'email': email_str,
                        'address': result.get('address', ''),
                        'legal_representative': result.get('legal_representative', ''),
                        'registered_capital': result.get('registered_capital', ''),
                        'established_date': result.get('established_date', ''),
                        'business_scope': result.get('business_scope', '')
                    }
                    writer.writerow(row)
                
                print(f"✅ 結果已保存到: {filename}")
                print(f"📊 共保存 {len(self.all_results)} 家公司的聯絡資料")
                
        except Exception as e:
            print(f"❌ 保存CSV失敗: {str(e)}")
    
    async def run_batch_search(self):
        """運行批量搜索"""
        print("🚀 開始批量公司聯絡資料搜索")
        
        # 載入公司列表
        companies = self.load_company_list()
        
        if not companies:
            print("❌ 沒有公司需要處理")
            return
        
        # 設置瀏覽器
        await self.setup_browser()
        
        # 訪問百度AI
        if not await self.access_baidu_ai():
            print("❌ 無法訪問百度AI，批量搜索終止")
            return
        
        # 開始批量處理
        total_companies = len(companies)
        successful_searches = 0
        
        print(f"📋 開始處理 {total_companies} 家公司...")
        
        for i, company_name in enumerate(companies, 1):
            try:
                print(f"\n{'='*60}")
                print(f"處理進度: {i}/{total_companies} ({i/total_companies*100:.1f}%)")
                print(f"當前公司: {company_name}")
                
                # 搜索公司
                contact_info = await self.search_single_company(company_name)
                
                if contact_info:
                    self.all_results.append(contact_info)
                    successful_searches += 1
                    print(f"✅ 成功 ({successful_searches}/{i})")
                else:
                    print(f"❌ 失敗")
                
                # 標記為已處理
                self.processed_companies.add(company_name)
                
                # 每10個公司保存一次進度
                if i % 10 == 0:
                    self.save_progress()
                    self.save_results_to_csv(f"batch_progress_{i}.csv")
                
                # 延遲以避免被封鎖
                if i < total_companies:  # 不是最後一個公司
                    print(f"⏳ 等待 {self.batch_delay} 秒...")
                    await asyncio.sleep(self.batch_delay)
                
            except Exception as e:
                print(f"❌ 處理 {company_name} 時發生錯誤: {str(e)}")
                continue
        
        # 最終保存
        self.save_progress()
        self.save_results_to_csv()
        
        print(f"\n{'='*60}")
        print("🎉 批量搜索完成!")
        print(f"📊 總計處理: {total_companies} 家公司")
        print(f"✅ 成功獲取: {successful_searches} 家公司聯絡資料")
        print(f"📈 成功率: {successful_searches/total_companies*100:.1f}%")
        
        # 清理資源
        await self.cleanup()
    
    async def cleanup(self):
        """清理資源"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("🧹 資源清理完成")
        except:
            pass


async def main():
    """主函數"""
    print("🌟 批量公司聯絡資料搜索系統")
    print("=" * 50)
    
    searcher = BatchCompanySearch()
    await searcher.run_batch_search()


if __name__ == "__main__":
    asyncio.run(main()) 