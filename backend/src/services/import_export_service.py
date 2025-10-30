"""导入导出服务.

负责解析各种格式的文件并批量导入知识库。
支持格式：JSON, CSV, Excel, TXT, Markdown, PDF

解析逻辑：
- JSON: 数组中的每个对象 = 1条知识
- CSV/Excel: 除了表头外的每一行 = 1条知识
- TXT: 每一行 = 1条知识
- Markdown: 每个 ## 标题块 = 1条知识
- PDF: 每一页 = 1条知识
"""

import json
import csv
import io
from typing import List, Dict, Any, Optional
from pathlib import Path

import pandas as pd
from PyPDF2 import PdfReader

from ..models.schemas import KnowledgeCreate
from ..utils import logger


class ImportExportService:
    """导入导出服务类.
    
    功能：
    1. 解析多种格式的文件（JSON/CSV/Excel/TXT/Markdown）
    2. 批量导入知识库
    3. 导出知识库数据
    """
    
    def detect_file_format(self, filename: str) -> str:
        """检测文件格式.
        
        Args:
            filename: 文件名
            
        Returns:
            格式名称：json, csv, excel, txt, markdown
        """
        ext = Path(filename).suffix.lower()
        
        format_map = {
            '.json': 'json',
            '.csv': 'csv',
            '.xlsx': 'excel',
            '.xls': 'excel',
            '.txt': 'txt',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.pdf': 'pdf',
        }
        
        return format_map.get(ext, 'txt')
    
    async def parse_json_file(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析 JSON 文件.
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            知识条目列表
        """
        try:
            content_str = file_content.decode('utf-8')
            data = json.loads(content_str)
            
            if not isinstance(data, list):
                raise ValueError('JSON 文件必须包含一个数组')
            
            result = []
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f'第 {idx + 1} 行：必须是对象')
                
                if 'content' not in item:
                    raise ValueError(f'第 {idx + 1} 行：缺少 content 字段')
                
                result.append({
                    'content': str(item.get('content', '')),
                    'category': str(item.get('category', '未分类')),
                    'title': item.get('title'),
                    'tags': item.get('tags', []),
                })
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f'JSON 解析失败: {str(e)}')
        except Exception as e:
            raise ValueError(f'解析 JSON 文件失败: {str(e)}')
    
    async def parse_csv_file(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析 CSV 文件.
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            知识条目列表
        """
        try:
            content_str = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(content_str))
            
            result = []
            for idx, row in enumerate(csv_reader):
                if 'content' not in row or not row['content']:
                    raise ValueError(f'第 {idx + 2} 行：缺少 content 字段')
                
                # 解析 tags（逗号分隔）
                tags = []
                if row.get('tags'):
                    tags = [tag.strip() for tag in row['tags'].split(',') if tag.strip()]
                
                result.append({
                    'content': row['content'],
                    'category': row.get('category', '未分类'),
                    'title': row.get('title', '').strip() or None,
                    'tags': tags,
                })
            
            return result
            
        except Exception as e:
            raise ValueError(f'解析 CSV 文件失败: {str(e)}')
    
    async def parse_excel_file(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析 Excel 文件.
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            知识条目列表
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
            
            # 检查必需的列
            if 'content' not in df.columns:
                raise ValueError('Excel 文件必须包含 content 列')
            
            result = []
            for idx, row in df.iterrows():
                content = str(row.get('content', '')).strip()
                if not content or content == 'nan':
                    continue  # 跳过空行
                
                # 解析 tags
                tags = []
                if 'tags' in row and pd.notna(row['tags']):
                    tags_str = str(row['tags'])
                    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                
                result.append({
                    'content': content,
                    'category': str(row.get('category', '未分类')).strip(),
                    'title': str(row.get('title', '')).strip() or None if 'title' in row else None,
                    'tags': tags,
                })
            
            return result
            
        except Exception as e:
            raise ValueError(f'解析 Excel 文件失败: {str(e)}')
    
    async def parse_txt_file(
        self,
        file_content: bytes,
        default_category: str = '未分类'
    ) -> List[Dict[str, Any]]:
        """解析 TXT 文件.
        
        Args:
            file_content: 文件内容（字节）
            default_category: 默认分类
            
        Returns:
            知识条目列表
        """
        try:
            content_str = file_content.decode('utf-8')
            lines = content_str.strip().split('\n')
            
            result = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 支持分隔符格式：分类|内容
                if '|' in line:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        category = parts[0].strip() or default_category
                        content = parts[1].strip()
                    else:
                        category = default_category
                        content = line
                else:
                    category = default_category
                    content = line
                
                if content:
                    result.append({
                        'content': content,
                        'category': category,
                        'title': None,
                        'tags': [],
                    })
            
            return result
            
        except Exception as e:
            raise ValueError(f'解析 TXT 文件失败: {str(e)}')
    
    async def parse_markdown_file(self, file_content: bytes) -> List[Dict[str, Any]]:
        """解析 Markdown 文件.
        
        Args:
            file_content: 文件内容（字节）
            
        Returns:
            知识条目列表
        """
        try:
            content_str = file_content.decode('utf-8')
            
            # 简单的 Markdown 解析逻辑
            # 支持格式：# 分类名称\n\n## 标题\n内容
            lines = content_str.split('\n')
            
            result = []
            current_category = '未分类'
            current_title = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                
                # 一级标题 = 分类
                if line.startswith('# ') and not line.startswith('##'):
                    # 保存上一条知识
                    if current_content:
                        result.append({
                            'content': '\n'.join(current_content).strip(),
                            'category': current_category,
                            'title': current_title,
                            'tags': [],
                        })
                    
                    current_category = line[2:].strip()
                    current_title = None
                    current_content = []
                
                # 二级标题 = 知识标题
                elif line.startswith('## '):
                    # 保存上一条知识
                    if current_content:
                        result.append({
                            'content': '\n'.join(current_content).strip(),
                            'category': current_category,
                            'title': current_title,
                            'tags': [],
                        })
                    
                    current_title = line[3:].strip()
                    current_content = []
                
                # 内容
                elif line:
                    current_content.append(line)
            
            # 保存最后一条知识
            if current_content:
                result.append({
                    'content': '\n'.join(current_content).strip(),
                    'category': current_category,
                    'title': current_title,
                    'tags': [],
                })
            
            return result
            
        except Exception as e:
            raise ValueError(f'解析 Markdown 文件失败: {str(e)}')
    
    async def parse_pdf_file(
        self,
        file_content: bytes,
        default_category: str = '未分类'
    ) -> List[Dict[str, Any]]:
        """解析 PDF 文件.
        
        Args:
            file_content: 文件内容（字节）
            default_category: 默认分类
            
        Returns:
            知识条目列表
        """
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            
            result = []
            
            # 提取每一页的文本
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        # 清理文本（移除多余空白）
                        cleaned_text = ' '.join(text.split())
                        
                        if cleaned_text:
                            result.append({
                                'content': cleaned_text,
                                'category': default_category,
                                'title': f'PDF 第 {page_num + 1} 页',
                                'tags': [],
                            })
                except Exception as e:
                    logger.warning(f'提取 PDF 第 {page_num + 1} 页失败: {e}')
                    continue
            
            if not result:
                raise ValueError('PDF 文件中没有提取到任何文本内容')
            
            return result
            
        except Exception as e:
            raise ValueError(f'解析 PDF 文件失败: {str(e)}')
    
    async def parse_file(
        self,
        file_content: bytes,
        filename: str,
        format: Optional[str] = None,
        default_category: str = '未分类'
    ) -> List[Dict[str, Any]]:
        """解析文件（自动检测格式）.
        
        Args:
            file_content: 文件内容（字节）
            filename: 文件名
            format: 指定格式（可选，auto 表示自动检测）
            default_category: 默认分类（用于 TXT）
            
        Returns:
            知识条目列表
        """
        # 检测格式
        if format is None or format == 'auto':
            format = self.detect_file_format(filename)
        
        logger.info(f'解析文件: {filename}, 格式: {format}')
        
        # 根据格式解析
        if format == 'json':
            return await self.parse_json_file(file_content)
        elif format == 'csv':
            return await self.parse_csv_file(file_content)
        elif format == 'excel':
            return await self.parse_excel_file(file_content)
        elif format == 'txt':
            return await self.parse_txt_file(file_content, default_category)
        elif format == 'markdown':
            return await self.parse_markdown_file(file_content)
        elif format == 'pdf':
            return await self.parse_pdf_file(file_content, default_category)
        else:
            raise ValueError(f'不支持的格式: {format}')

