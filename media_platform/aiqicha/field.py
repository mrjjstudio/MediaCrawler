# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from enum import Enum


class SearchSortType(Enum):
    """搜索排序类型"""
    RELEVANCE = "relevance"      # 相关度排序
    REGISTER_TIME = "register_time"  # 注册时间排序
    CAPITAL = "capital"          # 注册资本排序
    

class CompanyStatus(Enum):
    """企业状态"""
    ACTIVE = "存续"
    CANCELLED = "注销"
    REVOKED = "吊销"
    MOVED_OUT = "迁出"
    SUSPENDED = "停业"
    MERGED = "合并"
    DISSOLVED = "解散"
    OTHER = "其他"


class CompanyType(Enum):
    """企业类型"""
    LIMITED_LIABILITY = "有限责任公司"
    JOINT_STOCK = "股份有限公司"
    INDIVIDUAL = "个人独资企业"
    PARTNERSHIP = "合伙企业"
    STATE_OWNED = "国有企业"
    FOREIGN_INVESTED = "外商投资企业"
    OTHER = "其他"


class IndustryType(Enum):
    """行业类型"""
    TECHNOLOGY = "科技"
    FINANCE = "金融"
    REAL_ESTATE = "房地产"
    MANUFACTURING = "制造业"
    WHOLESALE_RETAIL = "批发零售"
    CONSTRUCTION = "建筑业"
    TRANSPORTATION = "交通运输"
    ACCOMMODATION_CATERING = "住宿餐饮"
    EDUCATION = "教育"
    HEALTHCARE = "医疗"
    CULTURE_ENTERTAINMENT = "文化娱乐"
    OTHER = "其他"


class SearchFilterType(Enum):
    """搜索过滤条件"""
    ALL = "all"                  # 全部
    COMPANY_NAME = "company_name"  # 企业名称
    CREDIT_CODE = "credit_code"    # 统一社会信用代码
    LEGAL_PERSON = "legal_person"  # 法人姓名
    PHONE = "phone"              # 电话
    EMAIL = "email"              # 邮箱
    BRAND = "brand"              # 品牌
    PRODUCT = "product"          # 产品


class DataType(Enum):
    """数据类型"""
    BASIC_INFO = "basic_info"      # 基本信息
    SHAREHOLDER = "shareholder"    # 股东信息
    LEGAL_CASE = "legal_case"      # 法律诉讼
    INTELLECTUAL_PROPERTY = "intellectual_property"  # 知识产权
    BIDDING = "bidding"           # 招投标
    ANNUAL_REPORT = "annual_report"  # 年报
    CHANGE_RECORD = "change_record"  # 变更记录
    BRANCH = "branch"             # 分支机构
    RELATED_COMPANY = "related_company"  # 关联企业 