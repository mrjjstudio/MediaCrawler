#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
詳細調試2間公司搜索腳本
顯示完整的頁面內容和數據提取過程
"""

import asyncio
import csv
import re
from datetime import datetime
from batch_company_search import BatchCompanySearch


class Debug2Companies:
    """調試2間公司搜索"""
    
    def __init__(self):
        self.csv_filename = f"debug_2_companies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.create_csv_file()
    
    def create_csv_file(self):
        """創建CSV文件"""
        try:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'ai_response_length', 
                    'page_text_length', 'search_time'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                print(f"✅ CSV文件已創建: {self.csv_filename}")
        except Exception as e:
            print(f"❌ 創建CSV文件失敗: {str(e)}")
    
    def save_debug_content(self, filename: str, content: str):
        """保存調試內容到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 已保存調試內容到: {filename}")
        except Exception as e:
            print(f"❌ 保存調試內容失敗: {str(e)}")
    
    def enhanced_extract_phone(self, text: str) -> str:
        """增強版電話提取"""
        if not text:
            return ""
        
        # 更廣泛的電話號碼模式
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
                        print(f"   📞 找到電話號碼: {phone}")
                        return phone
        
        return ""
    
    def enhanced_extract_email(self, text: str) -> list:
        """增強版郵箱提取"""
        if not text:
            return []
        
        # 更廣泛的郵箱模式
        email_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'(?:邮箱|郵箱|email|Email|EMAIL)[:：\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        emails = []
        for pattern in email_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if '@' in match and '.' in match:
                    emails.append(match)
                    print(f"   📧 找到郵箱: {match}")
        
        return list(set(emails))  # 去重
    
    def enhanced_extract_address(self, text: str) -> str:
        """增強版地址提取"""
        if not text:
            return ""
        
        # 更廣泛的地址模式
        address_patterns = [
            r'(?:地址|地點|位置|Address|ADDRESS)[:：\s]*([^。\n\r]{10,100})',
            r'(?:位于|位於|在)([^。\n\r]{10,100})',
            r'([^。\n\r]*(?:市|區|县|縣|镇|鎮|街|路|号|號|栋|棟|楼|樓)[^。\n\r]{5,50})',
            r'([^。\n\r]*(?:工业区|工業區|开发区|開發區|产业园|產業園)[^。\n\r]{5,50})'
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    address = match.strip()
                    if len(address) >= 10:
                        print(f"   📍 找到地址: {address}")
                        return address
        
        return ""
    
    def enhanced_extract_legal_rep(self, text: str) -> str:
        """增強版法人提取"""
        if not text:
            return ""
        
        # 更廣泛的法人模式
        legal_patterns = [
            r'(?:法人|法定代表人|负责人|負責人|代表人)[:：\s]*([^。\n\r\s]{2,10})',
            r'(?:法人代表|法定代表)[:：\s]*([^。\n\r\s]{2,10})',
            r'([^。\n\r]*(?:是|为|為)([^。\n\r\s]{2,10}))',
        ]
        
        for pattern in legal_patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        name = match[-1]  # 取最後一個匹配組
                    else:
                        name = match
                    
                    name = name.strip()
                    if len(name) >= 2 and len(name) <= 10:
                        print(f"   👤 找到法人: {name}")
                        return name
        
        return ""
    
    async def debug_single_company(self, searcher, company_name: str, order: int):
        """調試單個公司搜索"""
        print(f"\n{'='*80}")
        print(f"🔍 調試公司 {order}: {company_name}")
        print("=" * 80)
        
        try:
            # 刷新頁面
            await searcher.page.reload(wait_until='networkidle')
            await searcher.page.wait_for_timeout(3000)
            
            # 搜索公司
            search_query = f"{company_name} 聯絡資料"
            print(f"🔍 搜索查詢: {search_query}")
            
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
            print("⏳ 等待AI回復...")
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
            
            print("✅ AI回復完成")
            
            # 獲取完整頁面內容
            full_page_text = await searcher.page.text_content('body')
            print(f"📄 完整頁面文本長度: {len(full_page_text)}")
            
            # 保存完整頁面內容
            page_filename = f"debug_page_{company_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
            self.save_debug_content(page_filename, full_page_text)
            
            # 獲取AI回答
            ai_response = await searcher.get_latest_ai_response()
            ai_length = len(ai_response) if ai_response else 0
            print(f"🤖 AI回答長度: {ai_length}")
            
            if ai_response:
                print(f"📝 AI回答內容:")
                print("-" * 50)
                print(ai_response)
                print("-" * 50)
                
                # 保存AI回答
                ai_filename = f"debug_ai_{company_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
                self.save_debug_content(ai_filename, ai_response)
            
            # 提取相關文本
            relevant_text = searcher.extract_relevant_text(full_page_text, company_name)
            print(f"🎯 相關文本長度: {len(relevant_text)}")
            
            if relevant_text:
                print(f"📝 相關文本片段:")
                print("-" * 50)
                print(relevant_text[:500] + "..." if len(relevant_text) > 500 else relevant_text)
                print("-" * 50)
                
                # 保存相關文本
                relevant_filename = f"debug_relevant_{company_name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.txt"
                self.save_debug_content(relevant_filename, relevant_text)
            
            # 使用增強版提取方法
            print("\n🔍 使用增強版提取方法:")
            phone = self.enhanced_extract_phone(relevant_text)
            emails = self.enhanced_extract_email(relevant_text)
            address = self.enhanced_extract_address(relevant_text)
            legal_rep = self.enhanced_extract_legal_rep(relevant_text)
            
            print(f"📞 最終電話: '{phone}'")
            print(f"📧 最終郵箱: {emails}")
            print(f"📍 最終地址: '{address}'")
            print(f"👤 最終法人: '{legal_rep}'")
            
            # 保存到CSV
            with open(self.csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'ai_response_length', 
                    'page_text_length', 'search_time'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                row = {
                    'company_name': company_name,
                    'phone': phone,
                    'email': '; '.join(emails) if emails else '',
                    'address': address,
                    'legal_representative': legal_rep,
                    'ai_response_length': ai_length,
                    'page_text_length': len(full_page_text),
                    'search_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                writer.writerow(row)
                print(f"💾 已保存到CSV: {company_name}")
            
            return {
                'phone': phone,
                'email': emails,
                'address': address,
                'legal_representative': legal_rep
            }
            
        except Exception as e:
            print(f"❌ 調試 {company_name} 失敗: {str(e)}")
            return None
    
    async def run_debug_2_companies(self):
        """運行2間公司調試"""
        print("🔍 開始詳細調試2間公司")
        print("=" * 80)
        
        # 載入前2間公司
        companies = []
        try:
            with open("companylist2.md", 'r', encoding='utf-8') as f:
                for line in f:
                    company = line.strip()
                    if company and not company.startswith('#'):
                        companies.append(company)
                        if len(companies) >= 2:
                            break
        except FileNotFoundError:
            print("❌ 公司列表文件不存在")
            return
        
        print(f"📋 調試公司列表:")
        for i, company in enumerate(companies, 1):
            print(f"   {i}. {company}")
        
        # 設置搜索實例
        searcher = BatchCompanySearch()
        
        try:
            # 設置瀏覽器
            await searcher.setup_browser()
            
            # 訪問百度AI
            if not await searcher.access_baidu_ai():
                print("❌ 無法訪問百度AI")
                return
            
            successful_count = 0
            
            # 調試每間公司
            for i, company_name in enumerate(companies, 1):
                result = await self.debug_single_company(searcher, company_name, i)
                
                if result and (result['phone'] or result['email'] or result['address']):
                    successful_count += 1
                    print(f"✅ 成功提取 {company_name} 的聯絡資料")
                else:
                    print(f"❌ 未能提取 {company_name} 的聯絡資料")
                
                # 延遲
                if i < len(companies):
                    print(f"⏳ 等待 5 秒...")
                    await asyncio.sleep(5)
            
            # 最終統計
            print(f"\n{'='*80}")
            print("🎉 調試完成!")
            print(f"📊 總計調試: {len(companies)} 家公司")
            print(f"✅ 成功提取: {successful_count} 家公司")
            print(f"📈 成功率: {successful_count/len(companies)*100:.1f}%")
            print(f"📄 結果文件: {self.csv_filename}")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ 調試過程中發生錯誤: {str(e)}")
        
        finally:
            # 清理資源
            await searcher.cleanup()


async def main():
    """主函數"""
    print("🔍 詳細調試2間公司搜索")
    print("=" * 50)
    
    # 確認開始
    confirm = input("🚀 確定開始調試嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 開始調試
    debugger = Debug2Companies()
    await debugger.run_debug_2_companies()


if __name__ == "__main__":
    asyncio.run(main()) 