# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。


class DataFetchError(Exception):
    """数据获取异常"""
    pass


class LoginError(Exception):
    """登录异常"""
    pass


class NetworkError(Exception):
    """网络请求异常"""
    pass


class ParseError(Exception):
    """数据解析异常"""
    pass


class RateLimitError(Exception):
    """请求频率限制异常"""
    pass


class CaptchaError(Exception):
    """验证码异常"""
    pass


class CompanyNotFoundError(Exception):
    """企业信息未找到异常"""
    pass


class PermissionError(Exception):
    """权限不足异常"""
    pass 