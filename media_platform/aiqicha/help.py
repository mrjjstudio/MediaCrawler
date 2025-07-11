# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

import re
import time
from typing import Dict, Optional, List
from urllib.parse import urlparse, parse_qs


def extract_company_id_from_url(url: str) -> Optional[str]:
    """
    从愛企查URL中提取企业ID
    Args:
        url: 愛企查企业详情页URL
    Returns:
        企业ID，如果提取失败返回None
    """
    try:
        # 匹配类似 https://aiqicha.baidu.com/company_detail_xxxxx 的URL
        pattern = r'company_detail_(\w+)'
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        
        # 匹配查询参数中的企业ID
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if 'companyId' in query_params:
            return query_params['companyId'][0]
        
        return None
    except Exception:
        return None


def parse_company_info_from_url(url: str) -> Dict:
    """
    从愛企查URL中解析企业信息
    Args:
        url: 愛企查企业详情页URL
    Returns:
        包含企业信息的字典
    """
    company_id = extract_company_id_from_url(url)
    return {
        'company_id': company_id,
        'source_url': url,
        'platform': 'aiqicha'
    }


def validate_credit_code(credit_code: str) -> bool:
    """
    验证统一社会信用代码格式
    Args:
        credit_code: 统一社会信用代码
    Returns:
        是否有效
    """
    if not credit_code:
        return False
    
    # 统一社会信用代码为18位，包含数字和字母
    pattern = r'^[0-9A-HJ-NPQRTUWXY]{2}[0-9]{6}[0-9A-HJ-NPQRTUWXY]{10}$'
    return bool(re.match(pattern, credit_code))


def format_currency(amount: str) -> Optional[float]:
    """
    格式化金额字符串为数字
    Args:
        amount: 金额字符串，如"100万元"、"1000.5万人民币"
    Returns:
        格式化后的金额（单位：元）
    """
    if not amount:
        return None
    
    try:
        # 移除空格和特殊字符
        amount = amount.strip().replace(',', '').replace('，', '')
        
        # 提取数字部分
        number_pattern = r'([\d.]+)'
        number_match = re.search(number_pattern, amount)
        if not number_match:
            return None
        
        number = float(number_match.group(1))
        
        # 处理单位
        if '万' in amount:
            number *= 10000
        elif '千' in amount:
            number *= 1000
        elif '亿' in amount:
            number *= 100000000
        
        return number
    except (ValueError, AttributeError):
        return None


def clean_company_name(name: str) -> str:
    """
    清理企业名称中的特殊字符
    Args:
        name: 原始企业名称
    Returns:
        清理后的企业名称
    """
    if not name:
        return ""
    
    # 移除常见的特殊字符和空格
    name = name.strip()
    name = re.sub(r'[\r\n\t]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    return name


def parse_date_string(date_str: str) -> Optional[str]:
    """
    解析各种格式的日期字符串
    Args:
        date_str: 日期字符串
    Returns:
        标准化的日期字符串 (YYYY-MM-DD)
    """
    if not date_str:
        return None
    
    try:
        # 匹配 YYYY-MM-DD 格式
        pattern1 = r'(\d{4})-(\d{1,2})-(\d{1,2})'
        match1 = re.search(pattern1, date_str)
        if match1:
            year, month, day = match1.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # 匹配 YYYY年MM月DD日 格式
        pattern2 = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        match2 = re.search(pattern2, date_str)
        if match2:
            year, month, day = match2.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # 匹配 YYYY/MM/DD 格式
        pattern3 = r'(\d{4})/(\d{1,2})/(\d{1,2})'
        match3 = re.search(pattern3, date_str)
        if match3:
            year, month, day = match3.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    except Exception:
        return None


def generate_search_id() -> str:
    """
    生成搜索ID
    Returns:
        唯一的搜索ID
    """
    return str(int(time.time() * 1000))


def parse_business_scope(scope: str) -> List[str]:
    """
    解析经营范围字符串
    Args:
        scope: 经营范围文本
    Returns:
        经营范围列表
    """
    if not scope:
        return []
    
    # 按照常见的分隔符拆分
    separators = [';', '；', '、', '，', ',', '\n']
    
    items = [scope]
    for sep in separators:
        temp = []
        for item in items:
            temp.extend(item.split(sep))
        items = temp
    
    # 清理和过滤空项
    result = []
    for item in items:
        item = item.strip()
        if item and len(item) > 2:  # 过滤掉太短的项
            result.append(item)
    
    return result


def calculate_company_score(company_info: Dict) -> int:
    """
    根据企业信息计算企业信用评分
    Args:
        company_info: 企业信息字典
    Returns:
        企业信用评分 (0-100)
    """
    score = 60  # 基础分
    
    # 注册资本加分
    if company_info.get('register_capital'):
        capital = format_currency(company_info['register_capital'])
        if capital:
            if capital >= 10000000:  # 1000万以上
                score += 20
            elif capital >= 1000000:  # 100万以上
                score += 15
            elif capital >= 100000:  # 10万以上
                score += 10
            else:
                score += 5
    
    # 企业状态加分
    if company_info.get('status') == '存续':
        score += 15
    elif company_info.get('status') in ['注销', '吊销']:
        score -= 30
    
    # 成立时间加分
    if company_info.get('establish_date'):
        try:
            from datetime import datetime
            establish_date = datetime.strptime(company_info['establish_date'], '%Y-%m-%d')
            years = (datetime.now() - establish_date).days / 365
            if years >= 10:
                score += 10
            elif years >= 5:
                score += 5
        except:
            pass
    
    return max(0, min(100, score))  # 确保分数在0-100之间 