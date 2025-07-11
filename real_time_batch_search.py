#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
實時批量公司搜索腳本
每搜索1間公司就立即保存1間的資料
"""

import asyncio
import csv
import json
import os
from datetime import datetime
from batch_company_search import BatchCompanySearch


class RealTimeBatchSearch:
    """實時批量公司搜索"""
    
    def __init__(self):
        self.csv_filename = f"real_time_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.progress_file = "real_time_progress.json"
        self.processed_companies = set()
        self.successful_count = 0
        self.total_count = 0
        
        # 創建CSV文件並寫入表頭
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
    
    async def run_real_time_search(self):
        """運行實時搜索"""
        print("🚀 開始實時批量搜索")
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
            
            # 開始實時搜索
            for i, company_name in enumerate(companies, 1):
                try:
                    print(f"\n{'='*60}")
                    print(f"🔍 搜索公司 {i}/{self.total_count}: {company_name}")
                    print(f"📊 當前成功率: {self.successful_count}/{i-1} ({self.successful_count/(i-1)*100:.1f}%)" if i > 1 else "📊 開始搜索...")
                    print("=" * 60)
                    
                    # 搜索公司
                    contact_info = await searcher.search_single_company(company_name)
                    
                    success = contact_info is not None
                    
                    if success:
                        self.successful_count += 1
                        print(f"✅ 成功找到聯絡資料:")
                        if contact_info:
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
            print("🎉 實時批量搜索完成!")
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
    print("🌟 實時批量公司搜索系統")
    print("每搜索1間公司就立即保存1間資料")
    print("=" * 50)
    
    # 確認開始
    confirm = input("🚀 確定開始實時批量搜索嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 開始實時搜索
    searcher = RealTimeBatchSearch()
    await searcher.run_real_time_search()


if __name__ == "__main__":
    asyncio.run(main()) 