#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最終版批量公司搜索腳本
每搜索1間就立即保存1間資料
使用修正後的數據提取邏輯
"""

import asyncio
import csv
import json
import os
import re
from datetime import datetime
from batch_company_search import BatchCompanySearch


class FinalBatchSearch:
    """最終版批量公司搜索"""
    
    def __init__(self):
        self.csv_filename = f"final_batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.progress_file = "final_batch_progress.json"
        self.processed_companies = set()
        self.successful_count = 0
        self.total_count = 0
        
        # 創建CSV文件
        self.create_csv_file()
        
        # 載入進度
        self.load_progress()
    
    def create_csv_file(self):
        """創建CSV文件並寫入表頭"""
        try:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'search_order', 'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'registered_capital', 
                    'established_date', 'business_scope', 'search_time', 'success'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                print(f"✅ CSV文件已創建: {self.csv_filename}")
        except Exception as e:
            print(f"❌ 創建CSV文件失敗: {str(e)}")
    
    def load_progress(self):
        """載入進度"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    progress_data = json.load(f)
                    self.processed_companies = set(progress_data.get('processed_companies', []))
                    self.successful_count = progress_data.get('successful_count', 0)
                    self.total_count = progress_data.get('total_count', 0)
                    print(f"📊 載入進度: 已處理 {len(self.processed_companies)} 家公司")
            except Exception as e:
                print(f"⚠️ 載入進度失敗: {str(e)}")
    
    def save_progress(self):
        """保存進度"""
        try:
            progress_data = {
                'processed_companies': list(self.processed_companies),
                'successful_count': self.successful_count,
                'total_count': self.total_count,
                'last_updated': datetime.now().isoformat(),
                'csv_filename': self.csv_filename
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ 保存進度失敗: {str(e)}")
    
    def enhanced_extract_phone(self, text: str) -> str:
        """增強版電話提取"""
        if not text:
            return ""
        
        # 更準確的電話號碼模式
        phone_patterns = [
            r'(?:电话|電話|手机|手機|联系电话|聯繫電話|Tel|TEL|Phone|PHONE)[:：\s]*([0-9\-\+\(\)\s]{8,20})',
            r'(?:Tel|TEL|电话|電話)[:：\s]*([0-9\-\+\(\)\s]{8,20})',
            r'([0-9]{3,4}[-\s]?[0-9]{7,8})',  # 座機格式
            r'([0-9]{11})',  # 手機格式
            r'(\+?[0-9]{1,4}[-\s]?[0-9]{3,4}[-\s]?[0-9]{4,8})',  # 國際格式
            r'([0-9]{4}[-\s]?[0-9]{8})'  # 0755-12345678 格式
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    # 清理電話號碼
                    phone = re.sub(r'[^\d\+\-\(\)]', '', match)
                    if len(phone) >= 8:
                        return phone
        
        return ""
    
    def enhanced_extract_email(self, text: str) -> list:
        """增強版郵箱提取"""
        if not text:
            return []
        
        # 更準確的郵箱模式
        email_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'(?:邮箱|郵箱|email|Email|EMAIL)[:：\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        emails = []
        for pattern in email_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if '@' in match and '.' in match:
                    emails.append(match)
        
        return list(set(emails))  # 去重
    
    def enhanced_extract_address(self, text: str) -> str:
        """增強版地址提取"""
        if not text:
            return ""
        
        # 更準確的地址模式
        address_patterns = [
            r'地址[:：\s]*([^。\n\r,，]{15,100}[市區县縣镇鎮街路号號栋棟楼樓室][^。\n\r,，]{0,50})',
            r'位于([^。\n\r,，]{15,100}[市區县縣镇鎮街路号號栋棟楼樓室][^。\n\r,，]{0,50})',
            r'([^。\n\r,，]{0,50}[市區县縣镇鎮][^。\n\r,，]{5,100}[街路号號栋棟楼樓室][^。\n\r,，]{0,50})',
            r'([^。\n\r,，]{0,50}[工业区工業區开发区開發區产业园產業園][^。\n\r,，]{5,100})',
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    address = match.strip()
                    # 過濾掉不合理的結果
                    if (len(address) >= 15 and 
                        not address.startswith('企业') and 
                        not address.startswith('公司') and
                        not address.endswith('信用') and
                        '阿里巴巴' not in address):
                        return address
        
        return ""
    
    def enhanced_extract_legal_rep(self, text: str) -> str:
        """增強版法人提取"""
        if not text:
            return ""
        
        # 更準確的法人模式
        legal_patterns = [
            r'法人[:：\s]*([^。\n\r,，\s]{2,8})',
            r'法定代表人[:：\s]*([^。\n\r,，\s]{2,8})',
            r'负责人[:：\s]*([^。\n\r,，\s]{2,8})',
            r'法人代表[:：\s]*([^。\n\r,，\s]{2,8})',
        ]
        
        for pattern in legal_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    name = match.strip()
                    # 過濾掉不合理的結果
                    if (len(name) >= 2 and len(name) <= 8 and 
                        not name.startswith('企业') and 
                        not name.startswith('公司') and
                        not name.endswith('信用') and
                        '阿里巴巴' not in name):
                        return name
        
        return ""
    
    def extract_contact_info(self, text: str) -> dict:
        """提取聯絡資料"""
        if not text:
            return None
        
        phone = self.enhanced_extract_phone(text)
        emails = self.enhanced_extract_email(text)
        address = self.enhanced_extract_address(text)
        legal_rep = self.enhanced_extract_legal_rep(text)
        
        # 如果沒有找到任何有效信息，返回None
        if not phone and not emails and not address and not legal_rep:
            return None
        
        return {
            'phone': phone,
            'email': emails,
            'address': address,
            'legal_representative': legal_rep,
            'registered_capital': '',
            'established_date': '',
            'business_scope': ''
        }
    
    async def search_single_company(self, searcher, company_name: str):
        """搜索單個公司"""
        try:
            # 刷新頁面
            await searcher.page.reload(wait_until='networkidle')
            await searcher.page.wait_for_timeout(3000)
            
            # 搜索公司
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
                    element = await searcher.page.query_selector(selector)
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
            await searcher.page.keyboard.press('Enter')
            
            # 等待AI回復
            await searcher.page.wait_for_timeout(8000)
            
            # 等待回復完成
            max_wait_time = 30
            wait_interval = 2
            waited_time = 0
            
            while waited_time < max_wait_time:
                page_text = await searcher.page.text_content('body')
                
                if "请等待" not in page_text and "回答中" not in page_text:
                    break
                
                await searcher.page.wait_for_timeout(wait_interval * 1000)
                waited_time += wait_interval
            
            # 獲取完整頁面內容
            full_page_text = await searcher.page.text_content('body')
            
            # 提取相關文本
            relevant_text = searcher.extract_relevant_text(full_page_text, company_name)
            
            # 提取聯絡資料
            contact_info = self.extract_contact_info(relevant_text)
            
            return contact_info
            
        except Exception as e:
            print(f"❌ 搜索 {company_name} 失敗: {str(e)}")
            return None
    
    def save_single_result(self, company_name: str, contact_info: dict, search_order: int, success: bool):
        """立即保存單個公司的結果"""
        try:
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'search_order', 'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'registered_capital', 
                    'established_date', 'business_scope', 'search_time', 'success'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # 處理郵箱數據
                if contact_info:
                    email_list = contact_info.get('email', [])
                    if isinstance(email_list, list):
                        email_str = '; '.join(email_list)
                    else:
                        email_str = email_list
                else:
                    email_str = ''
                
                # 構建行數據
                row = {
                    'search_order': search_order,
                    'company_name': company_name,
                    'phone': contact_info.get('phone', '') if contact_info else '',
                    'email': email_str,
                    'address': contact_info.get('address', '') if contact_info else '',
                    'legal_representative': contact_info.get('legal_representative', '') if contact_info else '',
                    'registered_capital': contact_info.get('registered_capital', '') if contact_info else '',
                    'established_date': contact_info.get('established_date', '') if contact_info else '',
                    'business_scope': contact_info.get('business_scope', '') if contact_info else '',
                    'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'success': 'Yes' if success else 'No'
                }
                
                writer.writerow(row)
                
                print(f"💾 已保存: {company_name} ({search_order}/{self.total_count})")
                
        except Exception as e:
            print(f"❌ 保存單個結果失敗: {str(e)}")
    
    def load_company_list(self):
        """載入公司列表"""
        companies = []
        
        try:
            with open("incomplete_companies_20250711_145854.md", 'r', encoding='utf-8') as f:
                for line in f:
                    company = line.strip()
                    if company and not company.startswith('#'):
                        companies.append(company)
            
            # 過濾掉已處理的公司
            remaining_companies = [c for c in companies if c not in self.processed_companies]
            
            print(f"📋 總公司數: {len(companies)}")
            print(f"📋 剩餘待處理: {len(remaining_companies)}")
            
            return remaining_companies
            
        except FileNotFoundError:
            print(f"❌ 公司列表文件不存在: companylist2.md")
            return []
    
    async def run_final_search(self):
        """運行最終搜索"""
        print("🚀 開始最終版批量搜索")
        print("每搜索1間公司就立即保存1間資料")
        print("=" * 60)
        
        # 載入公司列表
        companies = self.load_company_list()
        
        if not companies:
            print("❌ 沒有公司需要處理")
            return
        
        self.total_count = len(companies)
        
        # 設置搜索實例
        searcher = BatchCompanySearch()
        
        try:
            # 設置瀏覽器
            await searcher.setup_browser()
            
            # 訪問百度AI
            if not await searcher.access_baidu_ai():
                print("❌ 無法訪問百度AI")
                return
            
            # 開始最終搜索
            for i, company_name in enumerate(companies, 1):
                try:
                    print(f"\n{'='*60}")
                    print(f"🔍 搜索公司 {i}/{self.total_count}: {company_name}")
                    print(f"📊 當前成功率: {self.successful_count}/{i-1} ({self.successful_count/(i-1)*100:.1f}%)" if i > 1 else "📊 開始搜索...")
                    print("=" * 60)
                    
                    # 搜索公司
                    contact_info = await self.search_single_company(searcher, company_name)
                    
                    success = contact_info is not None
                    
                    if success:
                        self.successful_count += 1
                        print(f"✅ 成功找到聯絡資料:")
                        print(f"   📞 電話: {contact_info.get('phone', 'N/A')}")
                        
                        emails = contact_info.get('email', [])
                        if isinstance(emails, list) and emails:
                            print(f"   📧 郵箱: {'; '.join(emails)}")
                        elif emails:
                            print(f"   📧 郵箱: {emails}")
                        else:
                            print(f"   📧 郵箱: N/A")
                            
                        print(f"   📍 地址: {contact_info.get('address', 'N/A')}")
                        print(f"   👤 法人: {contact_info.get('legal_representative', 'N/A')}")
                    else:
                        print(f"❌ 未找到聯絡資料")
                    
                    # 立即保存結果
                    self.save_single_result(company_name, contact_info, i, success)
                    
                    # 更新進度
                    self.processed_companies.add(company_name)
                    self.save_progress()
                    
                    # 顯示實時統計
                    success_rate = self.successful_count / i * 100
                    print(f"📈 實時統計: {self.successful_count}/{i} 成功 ({success_rate:.1f}%)")
                    
                    # 延遲
                    if i < len(companies):
                        delay = 5  # 5秒延遲
                        print(f"⏳ 等待 {delay} 秒...")
                        await asyncio.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ 處理 {company_name} 時發生錯誤: {str(e)}")
                    
                    # 保存失敗記錄
                    self.save_single_result(company_name, None, i, False)
                    self.processed_companies.add(company_name)
                    self.save_progress()
                    continue
            
            # 最終統計
            print(f"\n{'='*60}")
            print("🎉 最終版批量搜索完成!")
            print(f"📊 總計處理: {len(companies)} 家公司")
            print(f"✅ 成功獲取: {self.successful_count} 家公司聯絡資料")
            print(f"📈 最終成功率: {self.successful_count/len(companies)*100:.1f}%")
            print(f"📄 結果文件: {self.csv_filename}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 搜索過程中發生錯誤: {str(e)}")
        
        finally:
            # 清理資源
            await searcher.cleanup()


async def main():
    """主函數"""
    print("🌟 最終版批量公司搜索系統")
    print("=" * 50)
    
    # 顯示提示
    print("📝 特點:")
    print("• 每搜索1間公司就立即保存1間資料")
    print("• 支持斷點續搜")
    print("• 使用修正後的數據提取邏輯")
    print("• 實時顯示進度和成功率")
    print()
    
    # 確認開始
    confirm = input("🚀 確定開始最終版批量搜索嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 開始最終搜索
    searcher = FinalBatchSearch()
    await searcher.run_final_search()


if __name__ == "__main__":
    asyncio.run(main()) 