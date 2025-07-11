#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試前5家公司的聯絡資料搜索腳本
"""

import asyncio
import csv
import os
from datetime import datetime
from batch_company_search import BatchCompanySearch


class Test5Companies:
    """測試前5家公司"""
    
    def __init__(self):
        self.test_companies = []
        self.results = []
        self.load_test_companies()
    
    def load_test_companies(self):
        """載入前5家公司"""
        try:
            with open("companylist2.md", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # 取前5家公司
                count = 0
                for line in lines:
                    company = line.strip()
                    if company and not company.startswith('#'):
                        self.test_companies.append(company)
                        count += 1
                        if count >= 5:
                            break
            
            print(f"📋 載入測試公司: {len(self.test_companies)} 家")
            for i, company in enumerate(self.test_companies, 1):
                print(f"  {i}. {company}")
            
        except FileNotFoundError:
            print("❌ 公司列表文件不存在")
            return
    
    async def run_test(self):
        """運行測試搜索"""
        if not self.test_companies:
            print("❌ 沒有測試公司")
            return
        
        print(f"\n🚀 開始測試搜索前5家公司...")
        print("=" * 60)
        
        # 創建搜索實例
        searcher = BatchCompanySearch()
        
        # 設置較短的延遲以加快測試
        searcher.batch_delay = 3  # 3秒延遲
        
        try:
            # 設置瀏覽器
            await searcher.setup_browser()
            
            # 訪問百度AI
            if not await searcher.access_baidu_ai():
                print("❌ 無法訪問百度AI")
                return
            
            # 開始測試每家公司
            successful_searches = 0
            
            for i, company_name in enumerate(self.test_companies, 1):
                print(f"\n{'='*60}")
                print(f"🔍 測試公司 {i}/5: {company_name}")
                print("=" * 60)
                
                try:
                    # 搜索公司
                    contact_info = await searcher.search_single_company(company_name)
                    
                    if contact_info:
                        self.results.append(contact_info)
                        successful_searches += 1
                        
                        # 顯示找到的信息
                        print(f"✅ 成功找到 {company_name} 的聯絡資料:")
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
                        print(f"❌ 未找到 {company_name} 的聯絡資料")
                    
                    # 延遲以避免被封鎖
                    if i < len(self.test_companies):
                        print(f"⏳ 等待 {searcher.batch_delay} 秒...")
                        await asyncio.sleep(searcher.batch_delay)
                
                except Exception as e:
                    print(f"❌ 搜索 {company_name} 時發生錯誤: {str(e)}")
                    continue
            
            # 保存測試結果
            self.save_test_results()
            
            # 顯示測試總結
            print(f"\n{'='*60}")
            print("🎉 測試完成!")
            print(f"📊 總計測試: {len(self.test_companies)} 家公司")
            print(f"✅ 成功獲取: {successful_searches} 家公司聯絡資料")
            print(f"📈 成功率: {successful_searches/len(self.test_companies)*100:.1f}%")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 測試過程中發生錯誤: {str(e)}")
        
        finally:
            # 清理資源
            await searcher.cleanup()
    
    def save_test_results(self):
        """保存測試結果"""
        if not self.results:
            print("⚠️ 沒有結果可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_5_companies_results_{timestamp}.csv"
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'company_name', 'phone', 'email', 'address', 
                    'legal_representative', 'registered_capital', 
                    'established_date', 'business_scope'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in self.results:
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
            
            print(f"✅ 測試結果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存測試結果失敗: {str(e)}")


async def main():
    """主函數"""
    print("🧪 測試前5家公司聯絡資料搜索")
    print("=" * 50)
    
    # 顯示將要測試的公司
    tester = Test5Companies()
    
    if not tester.test_companies:
        print("❌ 沒有找到測試公司")
        return
    
    # 確認是否開始測試
    print(f"\n準備測試以上 {len(tester.test_companies)} 家公司")
    print("預計需要時間: 約 5-10 分鐘")
    
    confirm = input("\n🚀 確定開始測試嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("測試已取消")
        return
    
    # 開始測試
    await tester.run_test()


if __name__ == "__main__":
    asyncio.run(main()) 