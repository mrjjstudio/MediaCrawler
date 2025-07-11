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
import json
import random
from typing import Dict, List, Optional
from urllib.parse import urlencode

import httpx
from playwright.async_api import BrowserContext

from base.base_crawler import AbstractApiClient
from tools import utils
from .exception import DataFetchError, NetworkError, RateLimitError
from .field import SearchSortType, SearchFilterType
from .help import generate_search_id


class AiqichaClient(AbstractApiClient):
    def __init__(self, 
                 timeout: int = 10, 
                 proxies: Optional[Dict] = None,
                 *,
                 headers: Optional[Dict] = None,
                 playwright_page=None,
                 cookie_str: str = "",
                 ):
        self.proxies = proxies
        self.timeout = timeout
        self.headers = headers or {}
        self._host = "https://aiqicha.baidu.com"
        self.playwright_page = playwright_page
        self.cookie_str = cookie_str
        
        # 默认请求头
        self.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://aiqicha.baidu.com/",
            "Origin": "https://aiqicha.baidu.com",
        })

    async def request(self, method: str, url: str, **kwargs) -> Dict:
        """
        发送HTTP请求
        Args:
            method: 请求方法
            url: 请求URL
            **kwargs: 其他请求参数
        Returns:
            响应数据字典
        """
        async with httpx.AsyncClient(proxies=self.proxies, timeout=self.timeout) as client:
            response = await client.request(
                method, url, headers=self.headers, **kwargs
            )
            if response.status_code != 200:
                raise NetworkError(f"Request failed with status code: {response.status_code}")
            
            try:
                return response.json()
            except json.JSONDecodeError:
                raise DataFetchError(f"Failed to decode JSON response: {response.text}")

    async def update_cookies(self, browser_context: BrowserContext):
        """
        更新cookies
        Args:
            browser_context: 浏览器上下文
        """
        cookie_str = await self.get_cookies(browser_context)
        self.headers["Cookie"] = cookie_str

    async def get_cookies(self, browser_context: BrowserContext) -> str:
        """
        获取cookies字符串
        Args:
            browser_context: 浏览器上下文
        Returns:
            cookies字符串
        """
        cookies = await browser_context.cookies()
        cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
        return cookie_str

    async def pong(self) -> bool:
        """
        检查连接状态
        Returns:
            连接是否正常
        """
        try:
            response = await self.request("GET", self._host)
            return response is not None
        except Exception:
            return False

    async def search_company(self, 
                           keyword: str, 
                           page: int = 1,
                           page_size: int = 20,
                           sort: SearchSortType = SearchSortType.RELEVANCE,
                           filter_type: SearchFilterType = SearchFilterType.ALL,
                           province: str = "",
                           city: str = "",
                           industry: str = "",
                           status: str = "",
                           **kwargs) -> Dict:
        """
        搜索企业
        Args:
            keyword: 搜索关键词
            page: 页码
            page_size: 每页数量
            sort: 排序方式
            filter_type: 过滤类型
            province: 省份
            city: 城市
            industry: 行业
            status: 企业状态
            **kwargs: 其他参数
        Returns:
            搜索结果
        """
        search_url = f"{self._host}/search"
        
        # 构建搜索参数
        params = {
            "q": keyword,
            "p": page,
            "size": page_size,
            "sort": sort.value,
            "filter": filter_type.value,
            "searchId": generate_search_id(),
        }
        
        # 添加可选参数
        if province:
            params["province"] = province
        if city:
            params["city"] = city
        if industry:
            params["industry"] = industry
        if status:
            params["status"] = status
        
        # 添加额外参数
        params.update(kwargs)
        
        try:
            # 模拟随机延迟
            await asyncio.sleep(random.uniform(1, 3))
            
            # 发送搜索请求
            response = await self.request("GET", search_url, params=params)
            
            # 解析响应
            if response.get("errno") != 0:
                raise DataFetchError(f"Search failed: {response.get('errmsg', 'Unknown error')}")
            
            return response.get("data", {})
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.search_company] Search error: {e}")
            raise DataFetchError(f"Failed to search company: {e}")

    async def get_company_detail(self, company_id: str) -> Dict:
        """
        获取企业详情
        Args:
            company_id: 企业ID
        Returns:
            企业详情数据
        """
        detail_url = f"{self._host}/company_detail_{company_id}"
        
        try:
            # 模拟随机延迟
            await asyncio.sleep(random.uniform(1, 2))
            
            # 获取企业详情页面
            response = await self.request("GET", detail_url)
            
            # 解析企业数据
            if self.playwright_page:
                await self.playwright_page.goto(detail_url)
                await self.playwright_page.wait_for_load_state("networkidle")
                
                # 提取企业基本信息
                company_data = await self._extract_company_data()
                return company_data
            else:
                # 如果没有浏览器页面，尝试从API获取
                api_url = f"{self._host}/api/company/detail"
                api_response = await self.request("GET", api_url, params={"id": company_id})
                return api_response.get("data", {})
                
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.get_company_detail] Get detail error: {e}")
            raise DataFetchError(f"Failed to get company detail: {e}")

    async def _extract_company_data(self) -> Dict:
        """
        从页面提取企业数据
        Returns:
            企业数据字典
        """
        if not self.playwright_page:
            return {}
        
        try:
            # 等待页面加载完成
            await self.playwright_page.wait_for_timeout(2000)
            
            # 提取基本信息
            company_data = {}
            
            # 企业名称
            try:
                company_name = await self.playwright_page.query_selector('.company-name')
                if company_name:
                    company_data['company_name'] = await company_name.text_content()
            except:
                pass
            
            # 法人代表
            try:
                legal_person = await self.playwright_page.query_selector('.legal-person')
                if legal_person:
                    company_data['legal_person'] = await legal_person.text_content()
            except:
                pass
            
            # 注册资本
            try:
                register_capital = await self.playwright_page.query_selector('.register-capital')
                if register_capital:
                    company_data['register_capital'] = await register_capital.text_content()
            except:
                pass
            
            # 成立日期
            try:
                establish_date = await self.playwright_page.query_selector('.establish-date')
                if establish_date:
                    company_data['establish_date'] = await establish_date.text_content()
            except:
                pass
            
            # 企业状态
            try:
                status = await self.playwright_page.query_selector('.company-status')
                if status:
                    company_data['status'] = await status.text_content()
            except:
                pass
            
            # 统一社会信用代码
            try:
                credit_code = await self.playwright_page.query_selector('.credit-code')
                if credit_code:
                    company_data['credit_code'] = await credit_code.text_content()
            except:
                pass
            
            # 经营范围
            try:
                business_scope = await self.playwright_page.query_selector('.business-scope')
                if business_scope:
                    company_data['business_scope'] = await business_scope.text_content()
            except:
                pass
            
            # 注册地址
            try:
                register_address = await self.playwright_page.query_selector('.register-address')
                if register_address:
                    company_data['register_address'] = await register_address.text_content()
            except:
                pass
            
            return company_data
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient._extract_company_data] Extract error: {e}")
            return {}

    async def get_company_shareholders(self, company_id: str) -> List[Dict]:
        """
        获取企业股东信息
        Args:
            company_id: 企业ID
        Returns:
            股东信息列表
        """
        try:
            shareholders_url = f"{self._host}/api/company/shareholders"
            response = await self.request("GET", shareholders_url, params={"id": company_id})
            
            if response.get("errno") != 0:
                raise DataFetchError(f"Get shareholders failed: {response.get('errmsg', 'Unknown error')}")
            
            return response.get("data", [])
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.get_company_shareholders] Get shareholders error: {e}")
            return []

    async def get_company_legal_cases(self, company_id: str, page: int = 1) -> Dict:
        """
        获取企业法律案件
        Args:
            company_id: 企业ID
            page: 页码
        Returns:
            法律案件数据
        """
        try:
            cases_url = f"{self._host}/api/company/legal_cases"
            params = {"id": company_id, "page": page}
            
            response = await self.request("GET", cases_url, params=params)
            
            if response.get("errno") != 0:
                raise DataFetchError(f"Get legal cases failed: {response.get('errmsg', 'Unknown error')}")
            
            return response.get("data", {})
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.get_company_legal_cases] Get legal cases error: {e}")
            return {}

    async def get_company_related_companies(self, company_id: str) -> List[Dict]:
        """
        获取关联企业
        Args:
            company_id: 企业ID
        Returns:
            关联企业列表
        """
        try:
            related_url = f"{self._host}/api/company/related"
            response = await self.request("GET", related_url, params={"id": company_id})
            
            if response.get("errno") != 0:
                raise DataFetchError(f"Get related companies failed: {response.get('errmsg', 'Unknown error')}")
            
            return response.get("data", [])
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.get_company_related_companies] Get related companies error: {e}")
            return []

    async def get_company_intellectual_property(self, company_id: str, page: int = 1) -> Dict:
        """
        获取企业知识产权信息
        Args:
            company_id: 企业ID
            page: 页码
        Returns:
            知识产权数据
        """
        try:
            ip_url = f"{self._host}/api/company/intellectual_property"
            params = {"id": company_id, "page": page}
            
            response = await self.request("GET", ip_url, params=params)
            
            if response.get("errno") != 0:
                raise DataFetchError(f"Get intellectual property failed: {response.get('errmsg', 'Unknown error')}")
            
            return response.get("data", {})
            
        except Exception as e:
            utils.logger.error(f"[AiqichaClient.get_company_intellectual_property] Get IP error: {e}")
            return {} 