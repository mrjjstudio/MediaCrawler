# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class AiqichaCompany:
    """愛企查企业信息模型"""
    company_id: str = ""                    # 企业ID
    company_name: str = ""                  # 企业名称
    legal_person: str = ""                  # 法人代表
    register_capital: str = ""              # 注册资本
    register_capital_amount: Optional[float] = None  # 注册资本数值
    establish_date: str = ""                # 成立日期
    status: str = ""                        # 企业状态
    credit_code: str = ""                   # 统一社会信用代码
    business_scope: str = ""                # 经营范围
    business_scope_list: List[str] = None   # 经营范围列表
    register_address: str = ""              # 注册地址
    company_type: str = ""                  # 企业类型
    industry: str = ""                      # 行业
    province: str = ""                      # 省份
    city: str = ""                          # 城市
    phone: str = ""                         # 联系电话
    email: str = ""                         # 邮箱
    website: str = ""                       # 官网
    company_score: int = 0                  # 企业评分
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳
    keyword: str = ""                       # 搜索关键词
    source_url: str = ""                    # 来源URL
    
    def __post_init__(self):
        if self.business_scope_list is None:
            self.business_scope_list = []


@dataclass
class AiqichaShareholder:
    """愛企查股东信息模型"""
    company_id: str = ""                    # 企业ID
    shareholder_name: str = ""              # 股东名称
    shareholder_type: str = ""              # 股东类型（个人/企业）
    investment_amount: str = ""             # 投资金额
    investment_amount_value: Optional[float] = None  # 投资金额数值
    investment_ratio: str = ""              # 投资比例
    investment_ratio_value: Optional[float] = None   # 投资比例数值
    investment_date: str = ""               # 投资日期
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaLegalCase:
    """愛企查法律案件模型"""
    company_id: str = ""                    # 企业ID
    case_id: str = ""                       # 案件ID
    case_title: str = ""                    # 案件标题
    case_type: str = ""                     # 案件类型
    case_status: str = ""                   # 案件状态
    case_date: str = ""                     # 案件日期
    court_name: str = ""                    # 法院名称
    case_amount: str = ""                   # 案件金额
    case_amount_value: Optional[float] = None        # 案件金额数值
    plaintiff: str = ""                     # 原告
    defendant: str = ""                     # 被告
    case_result: str = ""                   # 案件结果
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaIntellectualProperty:
    """愛企查知识产权模型"""
    company_id: str = ""                    # 企业ID
    ip_id: str = ""                         # 知识产权ID
    ip_name: str = ""                       # 知识产权名称
    ip_type: str = ""                       # 知识产权类型（专利/商标/著作权等）
    ip_status: str = ""                     # 状态
    application_date: str = ""              # 申请日期
    authorization_date: str = ""            # 授权日期
    application_number: str = ""            # 申请号
    authorization_number: str = ""          # 授权号
    ip_category: str = ""                   # 分类
    applicant: str = ""                     # 申请人
    inventor: str = ""                      # 发明人
    description: str = ""                   # 描述
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaBidding:
    """愛企查招投标模型"""
    company_id: str = ""                    # 企业ID
    bidding_id: str = ""                    # 招投标ID
    bidding_title: str = ""                 # 招投标标题
    bidding_type: str = ""                  # 招投标类型
    bidding_status: str = ""                # 状态
    publish_date: str = ""                  # 发布日期
    bidding_date: str = ""                  # 投标日期
    project_amount: str = ""                # 项目金额
    project_amount_value: Optional[float] = None     # 项目金额数值
    purchaser: str = ""                     # 采购方
    supplier: str = ""                      # 供应商
    winning_amount: str = ""                # 中标金额
    winning_amount_value: Optional[float] = None     # 中标金额数值
    project_description: str = ""           # 项目描述
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaAnnualReport:
    """愛企查年报模型"""
    company_id: str = ""                    # 企业ID
    report_year: str = ""                   # 年报年份
    report_type: str = ""                   # 年报类型
    report_status: str = ""                 # 年报状态
    report_date: str = ""                   # 报告日期
    revenue: str = ""                       # 营业收入
    revenue_value: Optional[float] = None   # 营业收入数值
    profit: str = ""                        # 利润
    profit_value: Optional[float] = None    # 利润数值
    assets: str = ""                        # 资产总额
    assets_value: Optional[float] = None    # 资产总额数值
    liabilities: str = ""                   # 负债总额
    liabilities_value: Optional[float] = None        # 负债总额数值
    employee_count: int = 0                 # 员工数量
    tax_amount: str = ""                    # 纳税金额
    tax_amount_value: Optional[float] = None         # 纳税金额数值
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaChangeRecord:
    """愛企查变更记录模型"""
    company_id: str = ""                    # 企业ID
    change_id: str = ""                     # 变更ID
    change_type: str = ""                   # 变更类型
    change_date: str = ""                   # 变更日期
    change_before: str = ""                 # 变更前
    change_after: str = ""                  # 变更后
    change_description: str = ""            # 变更描述
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaBranch:
    """愛企查分支机构模型"""
    company_id: str = ""                    # 企业ID
    branch_id: str = ""                     # 分支机构ID
    branch_name: str = ""                   # 分支机构名称
    branch_type: str = ""                   # 分支机构类型
    branch_status: str = ""                 # 状态
    establish_date: str = ""                # 成立日期
    legal_person: str = ""                  # 负责人
    register_address: str = ""              # 注册地址
    business_scope: str = ""                # 经营范围
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


@dataclass
class AiqichaRelatedCompany:
    """愛企查关联企业模型"""
    company_id: str = ""                    # 企业ID
    related_company_id: str = ""            # 关联企业ID
    related_company_name: str = ""          # 关联企业名称
    relation_type: str = ""                 # 关联类型
    relation_description: str = ""          # 关联描述
    investment_ratio: str = ""              # 投资比例
    investment_ratio_value: Optional[float] = None   # 投资比例数值
    platform: str = "aiqicha"              # 平台名称
    crawl_time: int = 0                     # 爬取时间戳


# 数据模型映射字典
AIQICHA_MODEL_MAP = {
    "company": AiqichaCompany,
    "shareholder": AiqichaShareholder,
    "legal_case": AiqichaLegalCase,
    "intellectual_property": AiqichaIntellectualProperty,
    "bidding": AiqichaBidding,
    "annual_report": AiqichaAnnualReport,
    "change_record": AiqichaChangeRecord,
    "branch": AiqichaBranch,
    "related_company": AiqichaRelatedCompany,
} 