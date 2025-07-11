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
from typing import Optional

from playwright.async_api import BrowserContext, Page

from base.base_crawler import AbstractLogin
from tools import utils
from .exception import LoginError, CaptchaError


class AiqichaLogin(AbstractLogin):
    def __init__(self, 
                 login_type: str,
                 login_phone: str, 
                 browser_context: BrowserContext,
                 context_page: Page,
                 cookie_str: str = "",
                 login_account: str = "",
                 login_password: str = ""):
        self.login_type = login_type
        self.login_phone = login_phone
        self.browser_context = browser_context
        self.context_page = context_page
        self.cookie_str = cookie_str
        self.login_account = login_account
        self.login_password = login_password

    async def begin(self):
        """开始登录流程"""
        utils.logger.info("[AiqichaLogin.begin] Begin login process")
        
        if self.login_type == "qrcode":
            await self.login_by_qrcode()
        elif self.login_type == "phone":
            await self.login_by_mobile()
        elif self.login_type == "cookie":
            await self.login_by_cookies()
        else:
            raise LoginError(f"Unsupported login type: {self.login_type}")

    async def login_by_qrcode(self):
        """二维码登录"""
        utils.logger.info("[AiqichaLogin.login_by_qrcode] Starting QR code login")
        
        try:
            # 导航到登录页面
            await self.context_page.goto("https://aiqicha.baidu.com/login")
            await self.context_page.wait_for_load_state("networkidle")
            
            # 等待二维码出现
            utils.logger.info("[AiqichaLogin.login_by_qrcode] Waiting for QR code")
            await self.context_page.wait_for_selector(".qrcode-img", timeout=10000)
            
            # 提示用户扫码
            utils.logger.info("[AiqichaLogin.login_by_qrcode] Please scan the QR code with your mobile device")
            
            # 等待登录成功
            await self._wait_for_login_success()
            
            utils.logger.info("[AiqichaLogin.login_by_qrcode] QR code login successful")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin.login_by_qrcode] QR code login failed: {e}")
            raise LoginError(f"QR code login failed: {e}")

    async def login_by_mobile(self):
        """手机号登录"""
        utils.logger.info("[AiqichaLogin.login_by_mobile] Starting mobile login")
        
        if not self.login_phone:
            raise LoginError("Phone number is required for mobile login")
        
        try:
            # 导航到登录页面
            await self.context_page.goto("https://aiqicha.baidu.com/login")
            await self.context_page.wait_for_load_state("networkidle")
            
            # 选择手机号登录
            await self.context_page.click(".phone-login-tab")
            await self.context_page.wait_for_timeout(1000)
            
            # 输入手机号
            phone_input = await self.context_page.query_selector(".phone-input")
            if phone_input:
                await phone_input.fill(self.login_phone)
            
            # 点击发送验证码
            await self.context_page.click(".send-code-btn")
            
            # 等待验证码输入
            utils.logger.info("[AiqichaLogin.login_by_mobile] Please enter the verification code")
            
            # 等待用户输入验证码并点击登录
            await self._wait_for_login_success()
            
            utils.logger.info("[AiqichaLogin.login_by_mobile] Mobile login successful")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin.login_by_mobile] Mobile login failed: {e}")
            raise LoginError(f"Mobile login failed: {e}")

    async def login_by_cookies(self):
        """Cookie登录"""
        utils.logger.info("[AiqichaLogin.login_by_cookies] Starting cookie login")
        
        if not self.cookie_str:
            raise LoginError("Cookie string is required for cookie login")
        
        try:
            # 解析cookie字符串
            cookies = self._parse_cookie_string(self.cookie_str)
            
            # 添加cookies到浏览器上下文
            await self.browser_context.add_cookies(cookies)
            
            # 导航到主页验证登录状态
            await self.context_page.goto("https://aiqicha.baidu.com/")
            await self.context_page.wait_for_load_state("networkidle")
            
            # 检查是否登录成功
            if await self._check_login_status():
                utils.logger.info("[AiqichaLogin.login_by_cookies] Cookie login successful")
            else:
                raise LoginError("Cookie login failed: Invalid or expired cookies")
                
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin.login_by_cookies] Cookie login failed: {e}")
            raise LoginError(f"Cookie login failed: {e}")

    async def _wait_for_login_success(self, timeout: int = 180):
        """等待登录成功"""
        utils.logger.info("[AiqichaLogin._wait_for_login_success] Waiting for login success")
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                raise LoginError("Login timeout")
            
            # 检查是否登录成功
            if await self._check_login_status():
                utils.logger.info("[AiqichaLogin._wait_for_login_success] Login success detected")
                return
            
            # 检查是否有验证码
            if await self._check_captcha():
                utils.logger.info("[AiqichaLogin._wait_for_login_success] Captcha detected, please solve it")
                await self._handle_captcha()
            
            await asyncio.sleep(2)

    async def _check_login_status(self) -> bool:
        """检查登录状态"""
        try:
            # 检查URL是否包含登录成功的标识
            current_url = self.context_page.url
            if "login" not in current_url:
                return True
            
            # 检查页面是否包含登录成功的元素
            user_info = await self.context_page.query_selector(".user-info")
            if user_info:
                return True
            
            # 检查是否有用户头像
            user_avatar = await self.context_page.query_selector(".user-avatar")
            if user_avatar:
                return True
            
            return False
            
        except Exception:
            return False

    async def _check_captcha(self) -> bool:
        """检查是否有验证码"""
        try:
            captcha_element = await self.context_page.query_selector(".captcha-container")
            return captcha_element is not None
        except Exception:
            return False

    async def _handle_captcha(self):
        """处理验证码"""
        utils.logger.info("[AiqichaLogin._handle_captcha] Handling captcha")
        
        try:
            # 等待用户手动处理验证码
            utils.logger.info("[AiqichaLogin._handle_captcha] Please solve the captcha manually")
            
            # 等待验证码消失
            await self.context_page.wait_for_function(
                "() => !document.querySelector('.captcha-container')",
                timeout=60000
            )
            
            utils.logger.info("[AiqichaLogin._handle_captcha] Captcha solved")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin._handle_captcha] Captcha handling failed: {e}")
            raise CaptchaError(f"Captcha handling failed: {e}")

    def _parse_cookie_string(self, cookie_str: str) -> list:
        """解析cookie字符串"""
        cookies = []
        
        if not cookie_str:
            return cookies
        
        try:
            # 解析cookie字符串
            cookie_pairs = cookie_str.split(';')
            
            for pair in cookie_pairs:
                if '=' in pair:
                    name, value = pair.strip().split('=', 1)
                    cookies.append({
                        'name': name.strip(),
                        'value': value.strip(),
                        'domain': '.aiqicha.baidu.com',
                        'path': '/',
                    })
            
            return cookies
            
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin._parse_cookie_string] Parse cookie error: {e}")
            return []

    async def check_login_state(self) -> bool:
        """检查登录状态"""
        try:
            await self.context_page.goto("https://aiqicha.baidu.com/")
            await self.context_page.wait_for_load_state("networkidle")
            
            return await self._check_login_status()
            
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin.check_login_state] Check login state error: {e}")
            return False

    async def get_login_cookies(self) -> str:
        """获取登录后的cookies"""
        try:
            cookies = await self.browser_context.cookies()
            cookie_str = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            return cookie_str
        except Exception as e:
            utils.logger.error(f"[AiqichaLogin.get_login_cookies] Get cookies error: {e}")
            return "" 