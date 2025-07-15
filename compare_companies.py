#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from datetime import datetime

def read_completed_companies(csv_file):
    """讀取已完成搜索的公司列表"""
    completed_companies = set()
    
    if not os.path.exists(csv_file):
        print(f"警告：CSV文件 {csv_file} 不存在")
        return completed_companies
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                company_name = row.get('company_name', '').strip()
                if company_name:
                    completed_companies.add(company_name)
    
    except Exception as e:
        print(f"讀取CSV文件時出錯：{e}")
    
    return completed_companies

def read_all_companies(md_file):
    """讀取完整的公司列表"""
    all_companies = []
    
    if not os.path.exists(md_file):
        print(f"錯誤：MD文件 {md_file} 不存在")
        return all_companies
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            for line in f:
                company_name = line.strip()
                if company_name:  # 跳過空行
                    all_companies.append(company_name)
    
    except Exception as e:
        print(f"讀取MD文件時出錯：{e}")
    
    return all_companies

def find_incomplete_companies(all_companies, completed_companies):
    """找出未完成的公司"""
    incomplete_companies = []
    
    for company in all_companies:
        if company not in completed_companies:
            incomplete_companies.append(company)
    
    return incomplete_companies

def save_incomplete_companies(incomplete_companies, output_file):
    """保存未完成的公司列表到新文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for company in incomplete_companies:
                f.write(f"{company}\n")
        print(f"未完成的公司列表已保存到：{output_file}")
    except Exception as e:
        print(f"保存文件時出錯：{e}")

def main():
    # 文件路徑
    csv_file = "final_batch_results_20250710_185207.csv"
    md_file = "companylist2.md"
    
    # 生成輸出文件名（帶時間戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"incomplete_companies_{timestamp}.md"
    
    print("=" * 60)
    print("公司列表對比分析")
    print("=" * 60)
    
    # 讀取已完成的公司
    print(f"1. 讀取已完成的公司（從 {csv_file}）...")
    completed_companies = read_completed_companies(csv_file)
    print(f"   已完成的公司數量：{len(completed_companies)}")
    
    # 讀取所有公司
    print(f"2. 讀取完整的公司列表（從 {md_file}）...")
    all_companies = read_all_companies(md_file)
    print(f"   總公司數量：{len(all_companies)}")
    
    # 找出未完成的公司
    print("3. 分析未完成的公司...")
    incomplete_companies = find_incomplete_companies(all_companies, completed_companies)
    print(f"   未完成的公司數量：{len(incomplete_companies)}")
    
    # 顯示統計信息
    print("\n" + "=" * 60)
    print("統計摘要")
    print("=" * 60)
    print(f"總公司數量：        {len(all_companies):,}")
    print(f"已完成數量：        {len(completed_companies):,}")
    print(f"未完成數量：        {len(incomplete_companies):,}")
    print(f"完成率：           {len(completed_companies)/len(all_companies)*100:.1f}%")
    print(f"剩餘工作量：        {len(incomplete_companies)/len(all_companies)*100:.1f}%")
    
    # 保存未完成的公司列表
    if incomplete_companies:
        print("\n4. 保存未完成的公司列表...")
        save_incomplete_companies(incomplete_companies, output_file)
        
        # 顯示前10個未完成的公司作為示例
        print("\n前10個未完成的公司（示例）：")
        for i, company in enumerate(incomplete_companies[:10], 1):
            print(f"   {i:2d}. {company}")
        
        if len(incomplete_companies) > 10:
            print(f"   ... 還有 {len(incomplete_companies) - 10} 個公司")
    else:
        print("\n🎉 太棒了！所有公司都已經完成搜索！")
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main() 