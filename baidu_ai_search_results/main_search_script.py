#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
優化的百度AI搜索腳本
使用簡潔的搜索詞獲取企業聯絡資料
支持多個郵箱地址提取
"""

import asyncio
from playwright.async_api import async_playwright
import json
import csv
import re
from datetime import datetime
from bs4 import BeautifulSoup


class OptimizedBaiduAISearch:
    """優化的百度AI搜索類"""
    
    def __init__(self):
        self.search_url = "https://chat.baidu.com/search?extParams=%7B%22enter_type%22%3A%22ai_explore_home%22%7D&isShowHello=1"
        self.playwright = None
        self.browser = None
        self.page = None
    
    async def setup_browser(self):
        """設置瀏覽器"""
        print("🚀 啟動優化的瀏覽器...")
        
        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=False,
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
    
    async def send_optimized_query(self, company_name: str):
        """發送優化的搜索查詢"""
        # 使用簡潔的搜索詞
        search_query = f"{company_name} 聯絡資料"
        print(f"🔍 優化搜索查詢: {search_query}")
        
        try:
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
                        print(f"✅ 找到輸入框: {selector}")
                        break
                except:
                    continue
            
            if not input_box:
                print("❌ 未找到輸入框")
                return False
            
            # 輸入搜索查詢
            await input_box.click()
            await input_box.fill("")
            await input_box.type(search_query)
            await self.page.keyboard.press('Enter')
            
            print("📤 優化查詢已發送，等待AI回復...")
            
            # 等待AI回復
            await self.page.wait_for_timeout(5000)
            
            # 智能等待AI完成回復
            max_wait_time = 60  # 優化等待時間為60秒
            wait_interval = 3   # 每3秒檢查一次
            waited_time = 0
            
            while waited_time < max_wait_time:
                print(f"⏳ 等待AI回復... ({waited_time}秒/{max_wait_time}秒)")
                
                # 檢查頁面狀態
                page_text = await self.page.text_content('body')
                
                # 檢查是否還在回復中
                if "请等待" not in page_text and "回答中" not in page_text:
                    # 檢查是否有聯絡資料相關內容
                    if self.has_contact_info(page_text):
                        print("✅ AI回復完成，找到聯絡資料！")
                        return True
                
                await self.page.wait_for_timeout(wait_interval * 1000)
                waited_time += wait_interval
            
            print("⏰ 等待超時，使用當前狀態")
            return True
            
        except Exception as e:
            print(f"❌ 發送優化查詢失敗: {str(e)}")
            return False
    
    def has_contact_info(self, page_text: str) -> bool:
        """檢查是否包含聯絡資料"""
        contact_keywords = [
            "电话", "電話", "聯絡", "联系", "邮箱", "郵箱", "地址", 
            "法定代表人", "注册资本", "成立", "021-", "@", "有限公司"
        ]
        
        keyword_count = sum(1 for keyword in contact_keywords if keyword in page_text)
        
        # 如果包含5個或更多關鍵字，認為有聯絡資料
        if keyword_count >= 5:
            return True
        
        # 或者內容足夠豐富
        if len(page_text) > 3000:
            return True
        
        return False
    
    async def extract_contact_info(self, company_name: str):
        """提取聯絡資料"""
        print("📞 開始提取聯絡資料...")
        
        try:
            # 等待頁面穩定
            await self.page.wait_for_timeout(2000)
            
            # 獲取頁面內容
            html_content = await self.page.content()
            
            # 保存HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_filename = f"contact_search_{company_name}_{timestamp}.html"
            with open(html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"📄 HTML已保存: {html_filename}")
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 移除腳本和樣式
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 獲取純文本
            page_text = soup.get_text()
            
            # 保存純文本
            text_filename = f"contact_text_{company_name}_{timestamp}.txt"
            with open(text_filename, 'w', encoding='utf-8') as f:
                f.write(page_text)
            print(f"📄 純文本已保存: {text_filename}")
            
            # 提取聯絡資料
            contact_info = {
                'company_name': company_name,
                'search_query': f"{company_name} 聯絡資料",
                'search_timestamp': datetime.now().isoformat(),
                'html_file': html_filename,
                'text_file': text_filename
            }
            
            # 聯絡資料提取模式
            contact_patterns = {
                'legal_representative': [
                    r'法定代表人[：:\s]*([^\n\r，,。.；;\s]+)',
                    r'法人[：:\s]*([^\n\r，,。.；;\s]+)',
                    r'代表人[：:\s]*([^\n\r，,。.；;\s]+)',
                    r'负责人[：:\s]*([^\n\r，,。.；;\s]+)'
                ],
                'registered_capital': [
                    r'注册资本[：:\s]*([^\n\r，,。.；;]+)',
                    r'註冊資本[：:\s]*([^\n\r，,。.；;]+)',
                    r'资本[：:\s]*([^\n\r，,。.；;]+)'
                ],
                'establishment_date': [
                    r'成立[时间日期][：:\s]*([^\n\r，,。.；;]+)',
                    r'成立于[：:\s]*([^\n\r，,。.；;]+)',
                    r'成立.{0,5}([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)',
                    r'成立.{0,5}([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})'
                ],
                'address': [
                    r'地址[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'註冊地址[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'注册地址[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'办公地址[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'联系地址[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'(上海市[^\n\r]+?)(?=\n|$)',
                    r'(虹口区[^\n\r]+?)(?=\n|$)',
                    r'(浦东[^\n\r]+?)(?=\n|$)'
                ],
                'phone': [
                    r'电话[：:\s]*([^\n\r，,。.；;]+)',
                    r'聯繫電話[：:\s]*([^\n\r，,。.；;]+)',
                    r'联系电话[：:\s]*([^\n\r，,。.；;]+)',
                    r'Tel[：:\s]*([^\n\r，,。.；;]+)',
                    r'([0-9]{3,4}-[0-9]{7,8})',
                    r'([0-9]{11})',
                    r'(021-[0-9]{8})'
                ],
                'email': [
                    r'邮箱[：:\s]*([^\n\r，,。.；;]+)',
                    r'電子郵箱[：:\s]*([^\n\r，,。.；;]+)',
                    r'电子邮箱[：:\s]*([^\n\r，,。.；;]+)',
                    r'Email[：:\s]*([^\n\r，,。.；;]+)',
                    r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                ],
                'website': [
                    r'网站[：:\s]*([^\n\r，,。.；;]+)',
                    r'官网[：:\s]*([^\n\r，,。.；;]+)',
                    r'官方网站[：:\s]*([^\n\r，,。.；;]+)',
                    r'(https?://[^\s]+)',
                    r'(www\.[^\s]+)'
                ],
                'fax': [
                    r'传真[：:\s]*([^\n\r，,。.；;]+)',
                    r'傳真[：:\s]*([^\n\r，,。.；;]+)',
                    r'Fax[：:\s]*([^\n\r，,。.；;]+)',
                    r'(021-[0-9]{8})'
                ],
                'contact_person': [
                    r'联系人[：:\s]*([^\n\r，,。.；;]+)',
                    r'聯繫人[：:\s]*([^\n\r，,。.；;]+)',
                    r'负责人[：:\s]*([^\n\r，,。.；;]+)',
                    r'業務負責人[：:\s]*([^\n\r，,。.；;]+)'
                ],
                'business_scope': [
                    r'经营范围[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'經營範圍[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'主营业务[：:\s]*([^\n\r]+?)(?=\n|$)',
                    r'主要经营[：:\s]*([^\n\r]+?)(?=\n|$)'
                ],
                'social_credit_code': [
                    r'统一社会信用代码[：:\s]*([^\n\r，,。.；;]+)',
                    r'社会信用代码[：:\s]*([^\n\r，,。.；;]+)',
                    r'信用代码[：:\s]*([^\n\r，,。.；;]+)',
                    r'([0-9A-Z]{18})'
                ]
            }
            
            # 提取聯絡資料
            print("\n🔍 開始提取聯絡資料...")
            found_count = 0
            
            for field, pattern_list in contact_patterns.items():
                # 特殊處理郵箱 - 支持多個郵箱
                if field == 'email':
                    all_emails = []
                    for pattern in pattern_list:
                        try:
                            matches = re.findall(pattern, page_text, re.IGNORECASE)
                            if matches:
                                for match in matches:
                                    clean_email = self.clean_extracted_value(match)
                                    if '@' in clean_email and '.' in clean_email and len(clean_email) > 5:
                                        if clean_email not in all_emails:
                                            all_emails.append(clean_email)
                        except Exception as e:
                            continue
                    
                    if all_emails:
                        # 如果有多個郵箱，保留所有新的資料
                        contact_info['email'] = all_emails
                        found_count += 1
                        print(f"   ✅ 找到 {field}: {', '.join(all_emails)} (共{len(all_emails)}個)")
                
                else:
                    # 其他字段的正常處理
                    for pattern in pattern_list:
                        try:
                            matches = re.findall(pattern, page_text, re.IGNORECASE)
                            if matches:
                                # 選擇最合適的匹配
                                best_match = max(matches, key=len) if isinstance(matches[0], str) else matches[0]
                                clean_value = self.clean_extracted_value(best_match)
                                
                                if len(clean_value) > 1:
                                    contact_info[field] = clean_value
                                    found_count += 1
                                    print(f"   ✅ 找到 {field}: {clean_value}")
                                    break
                        except Exception as e:
                            continue
            
            # 特殊處理 - 修復常見格式問題
            if 'email' in contact_info:
                emails = contact_info['email']
                if isinstance(emails, list):
                    # 處理多個郵箱
                    fixed_emails = []
                    for email in emails:
                        if '@qq' in email and not email.endswith('.com'):
                            fixed_email = email + '.com'
                            fixed_emails.append(fixed_email)
                            print(f"   🔧 修復郵箱格式: {email} -> {fixed_email}")
                        else:
                            fixed_emails.append(email)
                    contact_info['email'] = fixed_emails
                else:
                    # 單個郵箱的處理
                    email = emails
                    if '@qq' in email and not email.endswith('.com'):
                        contact_info['email'] = email + '.com'
                        print(f"   🔧 修復郵箱格式: {contact_info['email']}")
            
            # 提取公司相關句子
            sentences = []
            for sentence in re.split(r'[。\n\r！？；]', page_text):
                if company_name in sentence and len(sentence.strip()) > 10:
                    clean_sentence = sentence.strip()
                    if clean_sentence and clean_sentence not in sentences:
                        sentences.append(clean_sentence)
            
            if sentences:
                contact_info['related_sentences'] = sentences[:10]
                print(f"   ✅ 找到相關句子: {len(sentences)} 個")
            
            print(f"✅ 聯絡資料提取完成，共找到 {found_count} 個聯絡字段")
            return contact_info
            
        except Exception as e:
            print(f"❌ 提取聯絡資料失敗: {str(e)}")
            return {}
    
    def clean_extracted_value(self, value: str) -> str:
        """清理提取的值"""
        if not value:
            return ""
        
        # 移除特殊字符
        value = re.sub(r'[‌\u200c\u200d\u202c\u202d\u2028\u2029]', '', str(value))
        
        # 移除多餘的空白
        value = re.sub(r'\s+', ' ', value).strip()
        
        # 移除前後的標點符號
        value = value.strip('：:，,。.；;')
        
        return value
    
    def save_contact_csv(self, contact_info: dict, filename: str):
        """保存聯絡資料到CSV"""
        print(f"💾 保存聯絡資料到CSV: {filename}")
        
        try:
            # 定義聯絡資料欄位
            fieldnames = [
                'company_name', 'legal_representative', 'registered_capital',
                'establishment_date', 'address', 'phone', 'email', 'website',
                'fax', 'contact_person', 'business_scope', 'social_credit_code',
                'search_query', 'search_timestamp', 'html_file', 'text_file'
            ]
            
            # 創建CSV文件
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # 準備數據行
                row_data = {}
                for field in fieldnames:
                    value = contact_info.get(field, '')
                    if isinstance(value, list):
                        value = '; '.join(str(v) for v in value)
                    row_data[field] = value
                
                writer.writerow(row_data)
            
            print(f"✅ 聯絡資料CSV已保存: {filename}")
            
            # 顯示聯絡資料摘要
            print("\n📞 聯絡資料摘要:")
            contact_fields = [
                ('公司名稱', 'company_name'),
                ('法定代表人', 'legal_representative'),
                ('聯繫地址', 'address'),
                ('聯繫電話', 'phone'),
                ('電子郵箱', 'email'),
                ('官方網站', 'website'),
                ('傳真號碼', 'fax'),
                ('聯繫人', 'contact_person'),
                ('註冊資本', 'registered_capital'),
                ('成立時間', 'establishment_date'),
                ('統一社會信用代碼', 'social_credit_code')
            ]
            
            for label, field in contact_fields:
                if field in contact_info and contact_info[field]:
                    value = contact_info[field]
                    if isinstance(value, list):
                        if field == 'email':
                            value = f"共{len(value)}個郵箱: {', '.join(value)}"
                        else:
                            value = '; '.join(str(v) for v in value)
                    value = str(value)
                    if len(value) > 100:
                        value = value[:100] + '...'
                    print(f"   {label}: {value}")
            
            return True
            
        except Exception as e:
            print(f"❌ 保存聯絡資料CSV失敗: {str(e)}")
            return False
    
    async def run_optimized_search(self, company_name: str):
        """運行優化搜索"""
        print("=" * 80)
        print(f"📞 開始優化搜索企業聯絡資料: {company_name}")
        print("🔍 搜索策略: 使用簡潔搜索詞 + 智能等待 + 多郵箱支持")
        print("=" * 80)
        
        try:
            # 設置瀏覽器
            await self.setup_browser()
            
            # 訪問百度AI
            access_ok = await self.access_baidu_ai()
            
            if access_ok:
                # 發送優化查詢
                query_ok = await self.send_optimized_query(company_name)
                
                if query_ok:
                    # 截圖查詢結果
                    await self.page.screenshot(path=f"optimized_result_{company_name}.png", full_page=True)
                    print(f"📸 優化結果截圖: optimized_result_{company_name}.png")
                    
                    # 提取聯絡資料
                    contact_info = await self.extract_contact_info(company_name)
                    
                    if contact_info:
                        # 保存為CSV
                        csv_filename = f"{company_name}_優化搜索聯絡資料.csv"
                        save_ok = self.save_contact_csv(contact_info, csv_filename)
                        
                        # 保存為JSON
                        json_filename = f"{company_name}_優化搜索聯絡資料.json"
                        with open(json_filename, 'w', encoding='utf-8') as f:
                            json.dump(contact_info, f, ensure_ascii=False, indent=2)
                        
                        print("\n" + "=" * 80)
                        print("📊 優化搜索結果:")
                        print(f"   頁面訪問: {'✅ 成功' if access_ok else '❌ 失敗'}")
                        print(f"   查詢發送: {'✅ 成功' if query_ok else '❌ 失敗'}")
                        print(f"   聯絡提取: {'✅ 成功' if contact_info else '❌ 失敗'}")
                        print(f"   CSV保存: {'✅ 成功' if save_ok else '❌ 失敗'}")
                        print(f"   聯絡字段: {len([k for k in contact_info.keys() if k not in ['search_timestamp', 'html_file', 'text_file', 'related_sentences', 'search_query']])} 個")
                        
                        # 顯示郵箱數量
                        if 'email' in contact_info:
                            emails = contact_info['email']
                            if isinstance(emails, list):
                                print(f"   郵箱數量: {len(emails)} 個")
                            else:
                                print(f"   郵箱數量: 1 個")
                        
                        print(f"   輸出文件: {csv_filename}, {json_filename}")
                        print("=" * 80)
                        
                        return contact_info
                    else:
                        print("❌ 未能提取到聯絡資料")
                        return {}
                else:
                    print("❌ 優化查詢失敗")
                    return {}
            else:
                print("❌ 頁面訪問失敗")
                return {}
                
        except Exception as e:
            print(f"❌ 優化搜索異常: {str(e)}")
            return {}
        finally:
            # 清理資源
            try:
                if self.page:
                    await self.page.close()
                if self.browser:
                    await self.browser.close()
                if self.playwright:
                    await self.playwright.stop()
            except:
                pass
    
    async def cleanup(self):
        """清理資源"""
        print("🧹 清理資源...")
        try:
            if self.page:
                await self.page.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass


async def main():
    """主函數"""
    company_name = "上海旭洲玩具有限公司"
    
    print("🚀 開始優化百度AI聯絡資料搜索...")
    print(f"🎯 目標公司: {company_name}")
    print(f"🔍 搜索查詢: {company_name} 聯絡資料")
    print("⚡ 優化特點: 簡潔搜索詞 + 智能等待 + 精準提取 + 多郵箱支持")
    
    searcher = OptimizedBaiduAISearch()
    result = await searcher.run_optimized_search(company_name)
    
    if result:
        print(f"\n🎉 優化搜索成功！")
        print(f"📄 查看聯絡資料: {company_name}_優化搜索聯絡資料.csv")
        print(f"📄 查看JSON數據: {company_name}_優化搜索聯絡資料.json")
        
        # 特別顯示郵箱資訊
        if 'email' in result:
            emails = result['email']
            if isinstance(emails, list):
                print(f"📧 找到 {len(emails)} 個郵箱:")
                for i, email in enumerate(emails, 1):
                    print(f"   {i}. {email}")
            else:
                print(f"📧 找到 1 個郵箱: {emails}")
        
    else:
        print("\n❌ 優化搜索失敗")
    
    print("\n💡 優化要點:")
    print("   • 使用簡潔搜索詞提高相關性")
    print("   • 智能等待AI完成回復")
    print("   • 專注提取聯絡資料")
    print("   • 支持多個郵箱地址提取")
    print("   • 自動修復常見格式問題")


if __name__ == "__main__":
    asyncio.run(main()) 