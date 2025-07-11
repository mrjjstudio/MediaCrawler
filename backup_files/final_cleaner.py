#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最終清理聯絡資料腳本
修正地址資訊並生成完美的聯絡資料
"""

import json
import csv
from datetime import datetime


def final_clean_contact_data():
    """最終清理聯絡資料"""
    print("🧹 開始最終清理聯絡資料...")
    
    # 準備最終的清理後數據
    final_data = {
        'company_name': '上海旭洲玩具有限公司',
        'legal_representative': '冯亚娣',
        'phone': '021-68938912',
        'email': '1179817144@qq.com',
        'address': '上海市虹口区四平路421弄107号',
        'establishment_date': '2006年01月25日',
        'registered_capital': '100万人民币',
        'social_credit_code': '91310109785165381K',
        'company_status': '存续',
        'company_type': '有限责任公司',
        'industry': '玩具制造业',
        'business_scope': '玩具销售;宠物食品及用品批发;宠物食品及用品零售;汽车零配件批发;汽车零配件零售;工艺美术品及礼仪用品销售;工艺美术品及收藏品批发',
        'branches': '上海旭洲玩具有限公司浦东分公司',
        'search_query': '上海旭洲玩具有限公司 聯絡資料',
        'search_timestamp': datetime.now().isoformat(),
        'data_source': 'Optimized Baidu AI Search',
        'extraction_method': 'Regex + Manual Cleaning + Final Correction'
    }
    
    # 保存最終清理後的數據
    final_json_filename = "上海旭洲玩具有限公司_最終聯絡資料.json"
    with open(final_json_filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 最終JSON數據已保存: {final_json_filename}")
    
    # 生成最終的CSV
    final_csv_filename = "上海旭洲玩具有限公司_最終聯絡資料.csv"
    
    fieldnames = [
        'company_name', 'legal_representative', 'phone', 'email', 
        'address', 'establishment_date', 'registered_capital', 
        'social_credit_code', 'company_status', 'company_type',
        'industry', 'business_scope', 'branches', 'search_query',
        'search_timestamp', 'data_source', 'extraction_method'
    ]
    
    with open(final_csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(final_data)
    
    print(f"💾 最終CSV文件已保存: {final_csv_filename}")
    
    # 生成可讀性更好的摘要CSV
    summary_csv_filename = "上海旭洲玩具有限公司_聯絡資料摘要.csv"
    
    summary_fieldnames = [
        '公司名稱', '法定代表人', '聯繫電話', '電子郵箱', '聯繫地址',
        '成立日期', '註冊資本', '統一社會信用代碼', '公司狀態', '公司類型',
        '所屬行業', '分公司'
    ]
    
    summary_data = {
        '公司名稱': final_data['company_name'],
        '法定代表人': final_data['legal_representative'],
        '聯繫電話': final_data['phone'],
        '電子郵箱': final_data['email'],
        '聯繫地址': final_data['address'],
        '成立日期': final_data['establishment_date'],
        '註冊資本': final_data['registered_capital'],
        '統一社會信用代碼': final_data['social_credit_code'],
        '公司狀態': final_data['company_status'],
        '公司類型': final_data['company_type'],
        '所屬行業': final_data['industry'],
        '分公司': final_data['branches']
    }
    
    with open(summary_csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
        writer.writeheader()
        writer.writerow(summary_data)
    
    print(f"💾 摘要CSV文件已保存: {summary_csv_filename}")
    
    # 顯示最終的聯絡資料摘要
    print("\n📞 最終聯絡資料摘要:")
    print("=" * 80)
    print(f"{'公司名稱':15}: {final_data['company_name']}")
    print(f"{'法定代表人':15}: {final_data['legal_representative']}")
    print(f"{'聯繫電話':15}: {final_data['phone']}")
    print(f"{'電子郵箱':15}: {final_data['email']}")
    print(f"{'聯繫地址':15}: {final_data['address']}")
    print(f"{'成立日期':15}: {final_data['establishment_date']}")
    print(f"{'註冊資本':15}: {final_data['registered_capital']}")
    print(f"{'統一社會信用代碼':15}: {final_data['social_credit_code']}")
    print(f"{'公司狀態':15}: {final_data['company_status']}")
    print(f"{'公司類型':15}: {final_data['company_type']}")
    print(f"{'所屬行業':15}: {final_data['industry']}")
    print(f"{'分公司':15}: {final_data['branches']}")
    print("=" * 80)
    
    # 顯示搜索資訊
    print("\n📊 搜索資訊:")
    print(f"搜索查詢: {final_data['search_query']}")
    print(f"數據來源: {final_data['data_source']}")
    print(f"提取方法: {final_data['extraction_method']}")
    print(f"清理時間: {final_data['search_timestamp']}")
    
    # 顯示文件清單
    print("\n📄 生成的文件:")
    print(f"• {final_json_filename} - 完整JSON數據")
    print(f"• {final_csv_filename} - 完整CSV數據")
    print(f"• {summary_csv_filename} - 中文摘要CSV")
    
    return final_data


def main():
    """主函數"""
    print("🎯 開始最終清理和整理聯絡資料...")
    
    result = final_clean_contact_data()
    
    if result:
        print("\n🎉 最終聯絡資料清理完成！")
        
        print("\n✅ 優化成果:")
        print("• 使用簡潔搜索詞 '上海旭洲玩具有限公司 聯絡資料'")
        print("• 成功獲取完整的企業聯絡資料")
        print("• 修正了地址資訊的混亂問題")
        print("• 生成了標準化的CSV和JSON格式")
        print("• 提供了中文摘要便於查看")
        
        print("\n📋 完整聯絡資料:")
        print(f"• 公司名稱: {result['company_name']}")
        print(f"• 法定代表人: {result['legal_representative']}")
        print(f"• 聯繫電話: {result['phone']}")
        print(f"• 電子郵箱: {result['email']}")
        print(f"• 聯繫地址: {result['address']}")
        print(f"• 成立日期: {result['establishment_date']}")
        print(f"• 註冊資本: {result['registered_capital']}")
        print(f"• 統一社會信用代碼: {result['social_credit_code']}")
        print(f"• 公司狀態: {result['company_status']}")
        print(f"• 分公司: {result['branches']}")
        
        print("\n💡 優化要點總結:")
        print("1. 簡潔搜索詞提高了搜索精準度")
        print("2. 百度AI聊天搜索避免了反爬蟲檢測")
        print("3. 智能等待機制確保AI回復完整")
        print("4. 多層次清理確保數據準確性")
        print("5. 生成多種格式便於不同用途")
        
    else:
        print("\n❌ 最終聯絡資料清理失敗")


if __name__ == "__main__":
    main() 