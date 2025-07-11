#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os

csv_file = "test_final_2_companies_184740.csv"

if os.path.exists(csv_file):
    print(f"📄 檢查文件: {csv_file}")
    print("=" * 60)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            print(f"第{i+1}行: {row}")
else:
    print(f"❌ 文件不存在: {csv_file}")
    print("📁 當前目錄的CSV文件:")
    for file in os.listdir('.'):
        if file.endswith('.csv'):
            print(f"   - {file}") 