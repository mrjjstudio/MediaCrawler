#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試最終版搜索效果
只測試前2家公司
"""

import asyncio
from final_batch_search import FinalBatchSearch


class TestFinal2Companies(FinalBatchSearch):
    """測試最終版搜索前2家公司"""
    
    def __init__(self):
        super().__init__()
        self.csv_filename = f"test_final_2_companies_{self.csv_filename.split('_')[-1]}"
        self.progress_file = "test_final_2_companies_progress.json"
        self.create_csv_file()
    
    def load_company_list(self):
        """載入前2家公司進行測試"""
        companies = []
        
        try:
            with open("companylist2.md", 'r', encoding='utf-8') as f:
                for line in f:
                    company = line.strip()
                    if company and not company.startswith('#'):
                        companies.append(company)
                        # 只取前2家進行測試
                        if len(companies) >= 2:
                            break
            
            # 過濾掉已處理的公司
            remaining_companies = [c for c in companies if c not in self.processed_companies]
            
            print(f"📋 測試公司數: {len(companies)}")
            print(f"📋 剩餘待處理: {len(remaining_companies)}")
            
            return remaining_companies
            
        except FileNotFoundError:
            print(f"❌ 公司列表文件不存在: companylist2.md")
            return []


async def main():
    """主函數"""
    print("🧪 測試最終版批量搜索系統")
    print("=" * 50)
    
    # 顯示提示
    print("📝 測試特點:")
    print("• 只測試前2家公司")
    print("• 每搜索1間就立即保存1間資料")
    print("• 使用修正後的數據提取邏輯")
    print("• 實時顯示進度和成功率")
    print()
    
    # 確認開始
    confirm = input("🚀 確定開始測試嗎？(y/N): ").strip().lower()
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 開始測試
    searcher = TestFinal2Companies()
    await searcher.run_final_search()


if __name__ == "__main__":
    asyncio.run(main()) 