# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：
# 1. 不得用于任何商业用途。
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。
# 3. 不得进行大规模爬取或对平台造成运营干扰。
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。
# 5. 不得用于任何非法或不当的用途。
#
# 详细许可条款请参阅项目根目录下的LICENSE文件。
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。

from typing import Dict

from db import AsyncMysqlDB
from tools import utils


class AiqichaStoreSQL:
    """愛企查SQL存储类"""
    
    def __init__(self):
        self.mysql_db = AsyncMysqlDB()
        
    async def add_company_info(self, company_info: Dict):
        """添加企业信息"""
        try:
            sql = """
            INSERT INTO aiqicha_company (
                company_id, company_name, legal_person, register_capital, 
                register_capital_amount, establish_date, status, credit_code,
                business_scope, register_address, company_type, industry,
                province, city, phone, email, website, company_score,
                platform, crawl_time, keyword, source_url
            ) VALUES (
                %(company_id)s, %(company_name)s, %(legal_person)s, %(register_capital)s,
                %(register_capital_amount)s, %(establish_date)s, %(status)s, %(credit_code)s,
                %(business_scope)s, %(register_address)s, %(company_type)s, %(industry)s,
                %(province)s, %(city)s, %(phone)s, %(email)s, %(website)s, %(company_score)s,
                %(platform)s, %(crawl_time)s, %(keyword)s, %(source_url)s
            ) ON DUPLICATE KEY UPDATE
                company_name = VALUES(company_name),
                legal_person = VALUES(legal_person),
                register_capital = VALUES(register_capital),
                register_capital_amount = VALUES(register_capital_amount),
                establish_date = VALUES(establish_date),
                status = VALUES(status),
                credit_code = VALUES(credit_code),
                business_scope = VALUES(business_scope),
                register_address = VALUES(register_address),
                company_type = VALUES(company_type),
                industry = VALUES(industry),
                province = VALUES(province),
                city = VALUES(city),
                phone = VALUES(phone),
                email = VALUES(email),
                website = VALUES(website),
                company_score = VALUES(company_score),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, company_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_company_info] Error: {e}")
            
    async def add_shareholder_info(self, shareholder_info: Dict):
        """添加股东信息"""
        try:
            sql = """
            INSERT INTO aiqicha_shareholder (
                company_id, shareholder_name, shareholder_type, investment_amount,
                investment_amount_value, investment_ratio, investment_ratio_value,
                investment_date, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(shareholder_name)s, %(shareholder_type)s, %(investment_amount)s,
                %(investment_amount_value)s, %(investment_ratio)s, %(investment_ratio_value)s,
                %(investment_date)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                shareholder_name = VALUES(shareholder_name),
                shareholder_type = VALUES(shareholder_type),
                investment_amount = VALUES(investment_amount),
                investment_amount_value = VALUES(investment_amount_value),
                investment_ratio = VALUES(investment_ratio),
                investment_ratio_value = VALUES(investment_ratio_value),
                investment_date = VALUES(investment_date),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, shareholder_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_shareholder_info] Error: {e}")
            
    async def add_legal_case_info(self, legal_case_info: Dict):
        """添加法律案件信息"""
        try:
            sql = """
            INSERT INTO aiqicha_legal_case (
                company_id, case_id, case_title, case_type, case_status,
                case_date, court_name, case_amount, case_amount_value,
                plaintiff, defendant, case_result, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(case_id)s, %(case_title)s, %(case_type)s, %(case_status)s,
                %(case_date)s, %(court_name)s, %(case_amount)s, %(case_amount_value)s,
                %(plaintiff)s, %(defendant)s, %(case_result)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                case_title = VALUES(case_title),
                case_type = VALUES(case_type),
                case_status = VALUES(case_status),
                case_date = VALUES(case_date),
                court_name = VALUES(court_name),
                case_amount = VALUES(case_amount),
                case_amount_value = VALUES(case_amount_value),
                plaintiff = VALUES(plaintiff),
                defendant = VALUES(defendant),
                case_result = VALUES(case_result),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, legal_case_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_legal_case_info] Error: {e}")
            
    async def add_intellectual_property_info(self, ip_info: Dict):
        """添加知识产权信息"""
        try:
            sql = """
            INSERT INTO aiqicha_intellectual_property (
                company_id, ip_id, ip_name, ip_type, ip_status,
                application_date, authorization_date, application_number,
                authorization_number, ip_category, applicant, inventor,
                description, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(ip_id)s, %(ip_name)s, %(ip_type)s, %(ip_status)s,
                %(application_date)s, %(authorization_date)s, %(application_number)s,
                %(authorization_number)s, %(ip_category)s, %(applicant)s, %(inventor)s,
                %(description)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                ip_name = VALUES(ip_name),
                ip_type = VALUES(ip_type),
                ip_status = VALUES(ip_status),
                application_date = VALUES(application_date),
                authorization_date = VALUES(authorization_date),
                application_number = VALUES(application_number),
                authorization_number = VALUES(authorization_number),
                ip_category = VALUES(ip_category),
                applicant = VALUES(applicant),
                inventor = VALUES(inventor),
                description = VALUES(description),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, ip_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_intellectual_property_info] Error: {e}")
            
    async def add_bidding_info(self, bidding_info: Dict):
        """添加招投标信息"""
        try:
            sql = """
            INSERT INTO aiqicha_bidding (
                company_id, bidding_id, bidding_title, bidding_type, bidding_status,
                publish_date, bidding_date, project_amount, project_amount_value,
                purchaser, supplier, winning_amount, winning_amount_value,
                project_description, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(bidding_id)s, %(bidding_title)s, %(bidding_type)s, %(bidding_status)s,
                %(publish_date)s, %(bidding_date)s, %(project_amount)s, %(project_amount_value)s,
                %(purchaser)s, %(supplier)s, %(winning_amount)s, %(winning_amount_value)s,
                %(project_description)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                bidding_title = VALUES(bidding_title),
                bidding_type = VALUES(bidding_type),
                bidding_status = VALUES(bidding_status),
                publish_date = VALUES(publish_date),
                bidding_date = VALUES(bidding_date),
                project_amount = VALUES(project_amount),
                project_amount_value = VALUES(project_amount_value),
                purchaser = VALUES(purchaser),
                supplier = VALUES(supplier),
                winning_amount = VALUES(winning_amount),
                winning_amount_value = VALUES(winning_amount_value),
                project_description = VALUES(project_description),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, bidding_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_bidding_info] Error: {e}")
            
    async def add_annual_report_info(self, annual_report_info: Dict):
        """添加年报信息"""
        try:
            sql = """
            INSERT INTO aiqicha_annual_report (
                company_id, report_year, report_type, report_status, report_date,
                revenue, revenue_value, profit, profit_value, assets, assets_value,
                liabilities, liabilities_value, employee_count, tax_amount,
                tax_amount_value, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(report_year)s, %(report_type)s, %(report_status)s, %(report_date)s,
                %(revenue)s, %(revenue_value)s, %(profit)s, %(profit_value)s, %(assets)s, %(assets_value)s,
                %(liabilities)s, %(liabilities_value)s, %(employee_count)s, %(tax_amount)s,
                %(tax_amount_value)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                report_type = VALUES(report_type),
                report_status = VALUES(report_status),
                report_date = VALUES(report_date),
                revenue = VALUES(revenue),
                revenue_value = VALUES(revenue_value),
                profit = VALUES(profit),
                profit_value = VALUES(profit_value),
                assets = VALUES(assets),
                assets_value = VALUES(assets_value),
                liabilities = VALUES(liabilities),
                liabilities_value = VALUES(liabilities_value),
                employee_count = VALUES(employee_count),
                tax_amount = VALUES(tax_amount),
                tax_amount_value = VALUES(tax_amount_value),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, annual_report_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_annual_report_info] Error: {e}")
            
    async def add_change_record_info(self, change_record_info: Dict):
        """添加变更记录信息"""
        try:
            sql = """
            INSERT INTO aiqicha_change_record (
                company_id, change_id, change_type, change_date, change_before,
                change_after, change_description, platform, crawl_time
            ) VALUES (
                %(company_id)s, %(change_id)s, %(change_type)s, %(change_date)s, %(change_before)s,
                %(change_after)s, %(change_description)s, %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                change_type = VALUES(change_type),
                change_date = VALUES(change_date),
                change_before = VALUES(change_before),
                change_after = VALUES(change_after),
                change_description = VALUES(change_description),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, change_record_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_change_record_info] Error: {e}")
            
    async def add_branch_info(self, branch_info: Dict):
        """添加分支机构信息"""
        try:
            sql = """
            INSERT INTO aiqicha_branch (
                company_id, branch_id, branch_name, branch_type, branch_status,
                establish_date, legal_person, register_address, business_scope,
                platform, crawl_time
            ) VALUES (
                %(company_id)s, %(branch_id)s, %(branch_name)s, %(branch_type)s, %(branch_status)s,
                %(establish_date)s, %(legal_person)s, %(register_address)s, %(business_scope)s,
                %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                branch_name = VALUES(branch_name),
                branch_type = VALUES(branch_type),
                branch_status = VALUES(branch_status),
                establish_date = VALUES(establish_date),
                legal_person = VALUES(legal_person),
                register_address = VALUES(register_address),
                business_scope = VALUES(business_scope),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, branch_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_branch_info] Error: {e}")
            
    async def add_related_company_info(self, related_company_info: Dict):
        """添加关联企业信息"""
        try:
            sql = """
            INSERT INTO aiqicha_related_company (
                company_id, related_company_id, related_company_name, relation_type,
                relation_description, investment_ratio, investment_ratio_value,
                platform, crawl_time
            ) VALUES (
                %(company_id)s, %(related_company_id)s, %(related_company_name)s, %(relation_type)s,
                %(relation_description)s, %(investment_ratio)s, %(investment_ratio_value)s,
                %(platform)s, %(crawl_time)s
            ) ON DUPLICATE KEY UPDATE
                related_company_name = VALUES(related_company_name),
                relation_type = VALUES(relation_type),
                relation_description = VALUES(relation_description),
                investment_ratio = VALUES(investment_ratio),
                investment_ratio_value = VALUES(investment_ratio_value),
                crawl_time = VALUES(crawl_time)
            """
            await self.mysql_db.execute(sql, related_company_info)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreSQL.add_related_company_info] Error: {e}") 