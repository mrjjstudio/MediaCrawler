#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
改進版批量公司搜索腳本
使用更有效的搜索策略，確保數據提取穩定性
"""

import asyncio
import csv
import json
import os
from datetime import datetime
from batch_company_search import BatchCompanySearch


class ImprovedBatchSearch:
    """改進版批量公司搜索"""
    
    def __init__(self):
        self.csv_filename = f"improved_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.progress_file = "improved_progress.json"
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
    
    async def search_company_with_multiple_strategies(self, searcher, company_name: str):
        """使用多種策略搜索公司"""
        print(f"🔍 開始多策略搜索: {company_name}")
        
        # 策略1: 搜索企業信息（較能獲得頁面文本）
        strategies = [
            f"{company_name} 企業信息",
            f"{company_name} 工商信息",
            f"{company_name} 公司信息",
            f"{company_name} 聯絡資料",
            f"{company_name} 電話 郵箱 地址"
        ]
        
        best_result = None
        best_score = 0
        
        for i, query in enumerate(strategies, 1):
            try:
                print(f"   📝 策略 {i}: {query}")
                
                # 刷新頁面
                await searcher.page.reload(wait_until='networkidle')
                await searcher.page.wait_for_timeout(2000)
                
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
                    print(f"   ❌ 未找到輸入框")
                    continue
                
                # 輸入搜索查詢
                await input_box.click()
                await input_box.fill("")
                await input_box.type(query)
                await searcher.page.keyboard.press('Enter')
                
                # 等待AI回復
                await searcher.page.wait_for_timeout(5000)
                
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
                
                # 獲取AI回答或頁面文本
                latest_response = await searcher.get_latest_ai_response()
                
                if not latest_response:
                    # 如果沒有AI回答，使用整個頁面文本
                    page_text = await searcher.page.text_content('body')
                    latest_response = page_text
                
                # 提取相關文本
                relevant_text = searcher.extract_relevant_text(latest_response, company_name)
                
                # 提取聯絡資料
                contact_info = self.extract_contact_info(relevant_text)
                
                # 評估結果質量
                score = self.evaluate_result_quality(contact_info)
                
                print(f"   📊 結果評分: {score}")
                
                if score > best_score:
                    best_score = score
                    best_result = contact_info
                    print(f"   ✅ 更新最佳結果 (評分: {score})")
                
                # 如果已經找到很好的結果，可以提前結束
                if score >= 3:  # 有電話、郵箱、地址任意3項以上
                    print(f"   🎯 找到高質量結果，提前結束")
                    break
                
                # 策略間延遲
                if i < len(strategies):
                    await asyncio.sleep(3)
                
            except Exception as e:
                print(f"   ❌ 策略 {i} 失敗: {str(e)}")
                continue
        
        return best_result
    
    def extract_contact_info(self, text: str) -> dict:
        """提取聯絡資料"""
        if not text:
            return None
        
        # 創建一個臨時搜索實例來使用提取方法
        searcher = BatchCompanySearch()
        
        phone = searcher.extract_phone(text)
        emails = searcher.extract_emails(text)
        address = searcher.extract_address(text)
        legal_rep = searcher.extract_legal_representative(text)
        
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
    
    def evaluate_result_quality(self, contact_info: dict) -> int:
        """評估結果質量 (0-5分)"""
        if not contact_info:
            return 0
        
        score = 0
        
        # 電話 (最重要)
        if contact_info.get('phone'):
            score += 2
        
        # 郵箱 (重要)
        if contact_info.get('email'):
            emails = contact_info['email']
            if isinstance(emails, list) and emails:
                score += 1
            elif emails:
                score += 1
        
        # 地址 (重要)
        if contact_info.get('address'):
            score += 1
        
        # 法人 (一般)
        if contact_info.get('legal_representative'):
            score += 1
        
        return score
    
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
            with open("companylist2.md", 'r', encoding='utf-8') as f:
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
    
    async def run_improved_search(self):
        """運行改進版搜索"""
        print("🚀 開始改進版批量搜索")
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
            
            # 開始改進版搜索
            for i, company_name in enumerate(companies, 1):
                try:
                    print(f"\n{'='*60}")
                    print(f"🔍 搜索公司 {i}/{self.total_count}: {company_name}")
                    print(f"📊 當前成功率: {self.successful_count}/{i-1} ({self.successful_count/(i-1)*100:.1f}%)" if i > 1 else "📊 開始搜索...")
                    print("=" * 60)
                    
                    # 使用多策略搜索
                    contact_info = await self.search_company_with_multiple_strategies(searcher, company_name)
                    
                    success = contact_info is not None
                    
                    if success:
                        self.successful_count += 1
                        score = self.evaluate_result_quality(contact_info)
                        print(f"✅ 成功找到聯絡資料 (質量評分: {score}/5):")
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
            print("🎉 改進版批量搜索完成!")
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
    print("🌟 改進版批量公司搜索系統")
    print("使用多策略搜索，每搜索1間就立即保存1間資料")
    print("=" * 50)
    
    # 確認開始
    confirm = input("🚀 確定開始改進版批量搜索嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 開始改進版搜索
    searcher = ImprovedBatchSearch()
    await searcher.run_improved_search()


if __name__ == "__main__":
    asyncio.run(main()) 