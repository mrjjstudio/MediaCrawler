# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

import asyncio
import random
import time
from asyncio import Task
from typing import Dict, List, Optional, Tuple

from playwright.async_api import BrowserContext, BrowserType, Page, Playwright, async_playwright
from tenacity import RetryError

import config
from base.base_crawler import AbstractCrawler
from proxy.proxy_ip_pool import IpInfoModel, create_ip_pool
from tools import utils
from tools.cdp_browser import CDPBrowserManager
from var import crawler_type_var, source_keyword_var

from .client import AiqichaClient
from .exception import DataFetchError
from .field import SearchSortType, SearchFilterType
from .help import extract_company_id_from_url, parse_company_info_from_url
from .login import AiqichaLogin


class AiqichaCrawler(AbstractCrawler):
    context_page: Page
    aiqicha_client: AiqichaClient
    browser_context: BrowserContext
    cdp_manager: Optional[CDPBrowserManager]

    def __init__(self) -> None:
        self.index_url = "https://aiqicha.baidu.com"
        self.user_agent = config.UA if config.UA else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        self.cdp_manager = None

    async def start(self) -> None:
        """启动爬虫"""
        playwright_proxy_format, httpx_proxy_format = None, None
        if config.ENABLE_IP_PROXY:
            ip_proxy_pool = await create_ip_pool(
                config.IP_PROXY_POOL_COUNT, enable_validate_ip=True
            )
            ip_proxy_info: IpInfoModel = await ip_proxy_pool.get_proxy()
            playwright_proxy_format, httpx_proxy_format = self.format_proxy_info(
                ip_proxy_info
            )

        async with async_playwright() as playwright:
            # 根据配置选择启动模式
            if config.ENABLE_CDP_MODE:
                utils.logger.info("[AiqichaCrawler] 使用CDP模式启动浏览器")
                self.browser_context = await self.launch_browser_with_cdp(
                    playwright, playwright_proxy_format, self.user_agent,
                    headless=config.CDP_HEADLESS
                )
            else:
                utils.logger.info("[AiqichaCrawler] 使用标准模式启动浏览器")
                # Launch a browser context.
                chromium = playwright.chromium
                self.browser_context = await self.launch_browser(
                    chromium, playwright_proxy_format, self.user_agent, headless=config.HEADLESS
                )

            # 添加反检测脚本
            await self.browser_context.add_init_script(path="libs/stealth.min.js")
            
            # 创建新页面
            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # 创建爱企查客户端
            self.aiqicha_client = await self.create_aiqicha_client(httpx_proxy_format)
            
            # 检查登录状态
            if not await self.aiqicha_client.pong():
                login_obj = AiqichaLogin(
                    login_type=config.LOGIN_TYPE,
                    login_phone="",  # 输入手机号
                    browser_context=self.browser_context,
                    context_page=self.context_page,
                    cookie_str=config.COOKIES,
                )
                await login_obj.begin()
                await self.aiqicha_client.update_cookies(
                    browser_context=self.browser_context
                )

            # 设置爬取类型
            crawler_type_var.set(config.CRAWLER_TYPE)
            
            if config.CRAWLER_TYPE == "search":
                # 搜索企业并获取详情
                await self.search()
            elif config.CRAWLER_TYPE == "detail":
                # 获取指定企业的详情
                await self.get_specified_companies()
            elif config.CRAWLER_TYPE == "related":
                # 获取关联企业信息
                await self.get_related_companies()
            else:
                pass

            utils.logger.info("[AiqichaCrawler.start] Aiqicha Crawler finished ...")

    async def search(self) -> None:
        """搜索企业"""
        utils.logger.info("[AiqichaCrawler.search] Begin search aiqicha keywords")
        
        aiqicha_limit_count = 20  # 每页固定数量
        if config.CRAWLER_MAX_NOTES_COUNT < aiqicha_limit_count:
            config.CRAWLER_MAX_NOTES_COUNT = aiqicha_limit_count
        
        start_page = config.START_PAGE
        
        for keyword in config.KEYWORDS.split(","):
            source_keyword_var.set(keyword)
            utils.logger.info(f"[AiqichaCrawler.search] Current search keyword: {keyword}")
            
            page = 1
            while (page - start_page + 1) * aiqicha_limit_count <= config.CRAWLER_MAX_NOTES_COUNT:
                if page < start_page:
                    utils.logger.info(f"[AiqichaCrawler.search] Skip page {page}")
                    page += 1
                    continue

                try:
                    utils.logger.info(f"[AiqichaCrawler.search] search aiqicha keyword: {keyword}, page: {page}")
                    
                    # 搜索企业
                    search_result = await self.aiqicha_client.search_company(
                        keyword=keyword,
                        page=page,
                        page_size=aiqicha_limit_count,
                        sort=SearchSortType.RELEVANCE,
                        filter_type=SearchFilterType.ALL
                    )
                    
                    utils.logger.info(f"[AiqichaCrawler.search] Search result: {search_result}")
                    
                    if not search_result or not search_result.get("items"):
                        utils.logger.info("No more content!")
                        break
                    
                    # 并发获取企业详情
                    semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
                    task_list = [
                        self.get_company_detail_async_task(
                            company_id=item.get("id"),
                            company_name=item.get("name"),
                            semaphore=semaphore,
                        )
                        for item in search_result.get("items", [])
                        if item.get("id")
                    ]
                    
                    company_details = await asyncio.gather(*task_list)
                    
                    # 处理企业详情数据
                    for company_detail in company_details:
                        if company_detail:
                            # 存储企业信息
                            await self.store_company_info(company_detail)
                            
                            # 获取股东信息
                            if config.ENABLE_GET_COMMENTS:  # 复用这个配置项
                                await self.get_company_shareholders_info(company_detail.get("company_id"))
                    
                    page += 1
                    
                except DataFetchError:
                    utils.logger.error("[AiqichaCrawler.search] Get company detail error")
                    break

    async def get_specified_companies(self) -> None:
        """获取指定企业的详情"""
        utils.logger.info("[AiqichaCrawler.get_specified_companies] Begin get specified companies")
        
        # 从配置中获取指定的企业ID或URL列表
        company_list = getattr(config, 'AIQICHA_SPECIFIED_COMPANY_LIST', [])
        
        if not company_list:
            utils.logger.info("[AiqichaCrawler.get_specified_companies] No specified companies found")
            return
        
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENCY_NUM)
        task_list = []
        
        for company_item in company_list:
            # 处理企业ID或URL
            if isinstance(company_item, str):
                if company_item.startswith("http"):
                    # 处理URL
                    company_id = extract_company_id_from_url(company_item)
                    if company_id:
                        task_list.append(
                            self.get_company_detail_async_task(
                                company_id=company_id,
                                company_name="",
                                semaphore=semaphore
                            )
                        )
                else:
                    # 处理直接的企业ID
                    task_list.append(
                        self.get_company_detail_async_task(
                            company_id=company_item,
                            company_name="",
                            semaphore=semaphore
                        )
                    )
        
        # 并发获取企业详情
        company_details = await asyncio.gather(*task_list)
        
        # 处理结果
        for company_detail in company_details:
            if company_detail:
                await self.store_company_info(company_detail)
                
                # 获取额外信息
                if config.ENABLE_GET_COMMENTS:
                    await self.get_company_shareholders_info(company_detail.get("company_id"))

    async def get_related_companies(self) -> None:
        """获取关联企业信息"""
        utils.logger.info("[AiqichaCrawler.get_related_companies] Begin get related companies")
        
        # 获取基础企业列表
        base_company_list = getattr(config, 'AIQICHA_SPECIFIED_COMPANY_LIST', [])
        
        for company_item in base_company_list:
            company_id = None
            if isinstance(company_item, str):
                if company_item.startswith("http"):
                    company_id = extract_company_id_from_url(company_item)
                else:
                    company_id = company_item
            
            if company_id:
                try:
                    # 获取关联企业
                    related_companies = await self.aiqicha_client.get_company_related_companies(company_id)
                    
                    # 处理关联企业数据
                    for related_company in related_companies:
                        await self.store_company_info(related_company)
                        
                except Exception as e:
                    utils.logger.error(f"[AiqichaCrawler.get_related_companies] Error: {e}")

    async def get_company_detail_async_task(self, 
                                          company_id: str,
                                          company_name: str,
                                          semaphore: asyncio.Semaphore) -> Optional[Dict]:
        """异步获取企业详情"""
        async with semaphore:
            try:
                utils.logger.info(f"[AiqichaCrawler.get_company_detail_async_task] Getting company detail: {company_id}")
                
                # 获取企业详情
                company_detail = await self.aiqicha_client.get_company_detail(company_id)
                
                if not company_detail:
                    utils.logger.warning(f"[AiqichaCrawler.get_company_detail_async_task] Company detail is empty: {company_id}")
                    return None
                
                # 添加额外信息
                company_detail.update({
                    "company_id": company_id,
                    "platform": "aiqicha",
                    "crawl_time": int(time.time()),
                    "keyword": source_keyword_var.get() if source_keyword_var.get() else "",
                })
                
                # 数据清洗
                company_detail = self.clean_company_data(company_detail)
                
                return company_detail
                
            except Exception as e:
                utils.logger.error(f"[AiqichaCrawler.get_company_detail_async_task] Error: {e}")
                return None

    async def get_company_shareholders_info(self, company_id: str) -> None:
        """获取企业股东信息"""
        try:
            utils.logger.info(f"[AiqichaCrawler.get_company_shareholders_info] Getting shareholders: {company_id}")
            
            shareholders = await self.aiqicha_client.get_company_shareholders(company_id)
            
            for shareholder in shareholders:
                # 添加额外信息
                shareholder.update({
                    "company_id": company_id,
                    "platform": "aiqicha",
                    "crawl_time": int(time.time()),
                })
                
                # 存储股东信息
                await self.store_shareholder_info(shareholder)
                
        except Exception as e:
            utils.logger.error(f"[AiqichaCrawler.get_company_shareholders_info] Error: {e}")

    def clean_company_data(self, company_data: Dict) -> Dict:
        """清洗企业数据"""
        try:
            # 清理企业名称
            if company_data.get("company_name"):
                company_data["company_name"] = company_data["company_name"].strip()
            
            # 格式化注册资本
            if company_data.get("register_capital"):
                from .help import format_currency
                formatted_capital = format_currency(company_data["register_capital"])
                if formatted_capital:
                    company_data["register_capital_amount"] = formatted_capital
            
            # 格式化日期
            if company_data.get("establish_date"):
                from .help import parse_date_string
                formatted_date = parse_date_string(company_data["establish_date"])
                if formatted_date:
                    company_data["establish_date"] = formatted_date
            
            # 解析经营范围
            if company_data.get("business_scope"):
                from .help import parse_business_scope
                scope_list = parse_business_scope(company_data["business_scope"])
                company_data["business_scope_list"] = scope_list
            
            # 计算企业评分
            from .help import calculate_company_score
            company_data["company_score"] = calculate_company_score(company_data)
            
            return company_data
            
        except Exception as e:
            utils.logger.error(f"[AiqichaCrawler.clean_company_data] Error: {e}")
            return company_data

    async def store_company_info(self, company_info: Dict) -> None:
        """存储企业信息"""
        try:
            # 这里需要根据实际的存储实现来调用
            # 暂时使用日志记录
            utils.logger.info(f"[AiqichaCrawler.store_company_info] Storing company: {company_info.get('company_name')}")
            
            # TODO: 实现实际的存储逻辑
            # await aiqicha_store.update_company_info(company_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaCrawler.store_company_info] Error: {e}")

    async def store_shareholder_info(self, shareholder_info: Dict) -> None:
        """存储股东信息"""
        try:
            utils.logger.info(f"[AiqichaCrawler.store_shareholder_info] Storing shareholder: {shareholder_info.get('name')}")
            
            # TODO: 实现实际的存储逻辑
            # await aiqicha_store.update_shareholder_info(shareholder_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaCrawler.store_shareholder_info] Error: {e}")

    @staticmethod
    def format_proxy_info(ip_proxy_info: IpInfoModel) -> Tuple[Optional[Dict], Optional[Dict]]:
        """格式化代理信息"""
        playwright_proxy = {
            "server": f"{ip_proxy_info.protocol}://{ip_proxy_info.ip}:{ip_proxy_info.port}",
            "username": ip_proxy_info.user,
            "password": ip_proxy_info.password,
        }
        httpx_proxy = f"{ip_proxy_info.protocol}://{ip_proxy_info.user}:{ip_proxy_info.password}@{ip_proxy_info.ip}:{ip_proxy_info.port}"
        return playwright_proxy, httpx_proxy

    async def create_aiqicha_client(self, httpx_proxy: Optional[str]) -> AiqichaClient:
        """创建爱企查客户端"""
        utils.logger.info("[AiqichaCrawler.create_aiqicha_client] Creating aiqicha client ...")
        
        client = AiqichaClient(
            proxies={"http://": httpx_proxy, "https://": httpx_proxy} if httpx_proxy else None,
            headers={
                "User-Agent": self.user_agent,
            },
            playwright_page=self.context_page,
            cookie_str=config.COOKIES,
        )
        
        return client

    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict],
                           user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """启动浏览器"""
        utils.logger.info("[AiqichaCrawler.launch_browser] Launching browser ...")
        
        browser_context = await chromium.launch_persistent_context(
            user_data_dir=config.USER_DATA_DIR % "aiqicha",
            accept_downloads=True,
            headless=headless,
            proxy=playwright_proxy,
            viewport={"width": 1920, "height": 1080},
            user_agent=user_agent,
        )
        
        return browser_context

    async def launch_browser_with_cdp(self, playwright: Playwright, playwright_proxy: Optional[Dict],
                                    user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """使用CDP模式启动浏览器"""
        utils.logger.info("[AiqichaCrawler.launch_browser_with_cdp] Launching browser with CDP ...")
        
        from tools.cdp_browser import CDPBrowserManager
        
        self.cdp_manager = CDPBrowserManager(
            debug_port=config.CDP_DEBUG_PORT,
            headless=headless,
            proxy=playwright_proxy,
            user_agent=user_agent,
        )
        
        browser_context = await self.cdp_manager.launch_browser(playwright)
        return browser_context

    async def close(self):
        """关闭浏览器"""
        utils.logger.info("[AiqichaCrawler.close] Closing browser ...")
        
        if self.cdp_manager:
            await self.cdp_manager.close()
        
        if hasattr(self, 'browser_context') and self.browser_context:
            await self.browser_context.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 