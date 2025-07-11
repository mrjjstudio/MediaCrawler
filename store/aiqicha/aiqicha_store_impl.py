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
import csv
import json
import os
from typing import Dict, List

import aiofiles

from tools import utils
from .aiqicha_store_sql import AiqichaStoreSQL


class AiqichaStoreImplement:
    """愛企查存储实现类"""
    
    def __init__(self):
        self.aiqicha_store_sql = AiqichaStoreSQL()
        self.batch_size = 100
        self.batch_data = []
        self.batch_lock = asyncio.Lock()
        
    async def update_company_info(self, company_info: Dict):
        """更新企业信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_company_info(company_info)
            
            # 批量存储到文件
            await self._add_to_batch(company_info, "company")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_company_info] Error: {e}")
            
    async def update_shareholder_info(self, shareholder_info: Dict):
        """更新股东信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_shareholder_info(shareholder_info)
            
            # 批量存储到文件
            await self._add_to_batch(shareholder_info, "shareholder")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_shareholder_info] Error: {e}")
            
    async def update_legal_case_info(self, legal_case_info: Dict):
        """更新法律案件信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_legal_case_info(legal_case_info)
            
            # 批量存储到文件
            await self._add_to_batch(legal_case_info, "legal_case")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_legal_case_info] Error: {e}")
            
    async def update_intellectual_property_info(self, ip_info: Dict):
        """更新知识产权信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_intellectual_property_info(ip_info)
            
            # 批量存储到文件
            await self._add_to_batch(ip_info, "intellectual_property")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_intellectual_property_info] Error: {e}")
            
    async def update_bidding_info(self, bidding_info: Dict):
        """更新招投标信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_bidding_info(bidding_info)
            
            # 批量存储到文件
            await self._add_to_batch(bidding_info, "bidding")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_bidding_info] Error: {e}")
            
    async def update_annual_report_info(self, annual_report_info: Dict):
        """更新年报信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_annual_report_info(annual_report_info)
            
            # 批量存储到文件
            await self._add_to_batch(annual_report_info, "annual_report")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_annual_report_info] Error: {e}")
            
    async def update_change_record_info(self, change_record_info: Dict):
        """更新变更记录信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_change_record_info(change_record_info)
            
            # 批量存储到文件
            await self._add_to_batch(change_record_info, "change_record")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_change_record_info] Error: {e}")
            
    async def update_branch_info(self, branch_info: Dict):
        """更新分支机构信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_branch_info(branch_info)
            
            # 批量存储到文件
            await self._add_to_batch(branch_info, "branch")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_branch_info] Error: {e}")
            
    async def update_related_company_info(self, related_company_info: Dict):
        """更新关联企业信息"""
        try:
            # 数据库存储
            await self.aiqicha_store_sql.add_related_company_info(related_company_info)
            
            # 批量存储到文件
            await self._add_to_batch(related_company_info, "related_company")
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement.update_related_company_info] Error: {e}")
            
    async def _add_to_batch(self, data: Dict, data_type: str):
        """添加数据到批次"""
        async with self.batch_lock:
            self.batch_data.append({
                'data': data,
                'type': data_type
            })
            
            # 当批次达到指定大小时，执行批量写入
            if len(self.batch_data) >= self.batch_size:
                await self._flush_batch()
                
    async def _flush_batch(self):
        """批量写入数据"""
        if not self.batch_data:
            return
            
        try:
            # 按类型分组数据
            grouped_data = {}
            for item in self.batch_data:
                data_type = item['type']
                if data_type not in grouped_data:
                    grouped_data[data_type] = []
                grouped_data[data_type].append(item['data'])
            
            # 分别写入不同类型的文件
            for data_type, data_list in grouped_data.items():
                await self._write_to_file(data_list, data_type)
                
            # 清空批次数据
            self.batch_data.clear()
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement._flush_batch] Error: {e}")
            
    async def _write_to_file(self, data_list: List[Dict], data_type: str):
        """写入文件"""
        try:
            # 创建输出目录
            output_dir = "data/aiqicha"
            os.makedirs(output_dir, exist_ok=True)
            
            # JSON格式输出
            json_file = os.path.join(output_dir, f"{data_type}.json")
            await self._write_json_file(json_file, data_list)
            
            # CSV格式输出
            csv_file = os.path.join(output_dir, f"{data_type}.csv")
            await self._write_csv_file(csv_file, data_list)
            
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement._write_to_file] Error: {e}")
            
    async def _write_json_file(self, file_path: str, data_list: List[Dict]):
        """写入JSON文件"""
        try:
            # 读取现有数据
            existing_data = []
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                    if content.strip():
                        existing_data = json.loads(content)
            
            # 合并新数据
            existing_data.extend(data_list)
            
            # 写入文件
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(existing_data, ensure_ascii=False, indent=2))
                
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement._write_json_file] Error: {e}")
            
    async def _write_csv_file(self, file_path: str, data_list: List[Dict]):
        """写入CSV文件"""
        try:
            if not data_list:
                return
                
            # 获取所有字段
            fieldnames = set()
            for data in data_list:
                fieldnames.update(data.keys())
            fieldnames = sorted(list(fieldnames))
            
            # 检查文件是否存在
            file_exists = os.path.exists(file_path)
            
            # 写入CSV文件
            async with aiofiles.open(file_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # 如果文件不存在，写入表头
                if not file_exists:
                    await f.write(','.join(fieldnames) + '\n')
                
                # 写入数据
                for data in data_list:
                    # 确保所有字段都存在
                    row = {field: data.get(field, '') for field in fieldnames}
                    # 转换为字符串并写入
                    row_str = ','.join([f'"{str(value).replace('"', '""')}"' for value in row.values()])
                    await f.write(row_str + '\n')
                    
        except Exception as e:
            utils.logger.error(f"[AiqichaStoreImplement._write_csv_file] Error: {e}")
            
    async def close(self):
        """关闭存储器，执行最后的批量写入"""
        async with self.batch_lock:
            if self.batch_data:
                await self._flush_batch()
                
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close() 