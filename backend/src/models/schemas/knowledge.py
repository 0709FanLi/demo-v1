"""知识库相关的Pydantic模型.

用于API请求和响应的数据验证。
遵守企业级规范：完整类型提示、字段验证、文档说明。
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator


class KnowledgeCreate(BaseModel):
    """创建知识库条目请求模型.
    
    Args:
        content: 知识内容（必填）
        category: 知识分类（如：产品介绍、技术文档）
        metadata: 自定义元数据
    """
    
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description='知识内容',
    )
    category: str = Field(
        default='通用',
        max_length=50,
        description='知识分类',
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description='知识标题（可选）',
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description='标签列表（可选）',
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description='自定义元数据',
    )
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """验证内容不为空白."""
        if not v.strip():
            raise ValueError('内容不能为空白')
        return v.strip()


class KnowledgeUpdate(BaseModel):
    """更新知识库条目请求模型.
    
    Args:
        content: 知识内容（可选）
        category: 知识分类（可选）
        title: 知识标题（可选）
        tags: 标签列表（可选）
    """
    
    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10000,
        description='知识内容',
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description='知识分类',
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description='知识标题',
    )
    tags: Optional[List[str]] = Field(
        None,
        description='标签列表',
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description='自定义元数据',
    )
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Optional[str]) -> Optional[str]:
        """验证内容不为空白."""
        if v is not None and not v.strip():
            raise ValueError('内容不能为空白')
        return v.strip() if v else None


class KnowledgeBase(BaseModel):
    """知识库条目完整模型.
    
    包含所有字段，用于内部处理。
    """
    
    id: str = Field(..., description='文档唯一ID')
    content: str = Field(..., description='知识内容')
    category: str = Field(..., description='知识分类')
    metadata: Dict[str, Any] = Field(default_factory=dict, description='元数据')
    created_at: datetime = Field(default_factory=datetime.now, description='创建时间')
    
    model_config = {
        'json_schema_extra': {
            'example': {
                'id': 'doc_abc123',
                'content': '我们的产品支持7天无理由退货',
                'category': '售后政策',
                'metadata': {'source': '官网', 'version': '1.0'},
                'created_at': '2024-01-01T00:00:00',
            }
        }
    }


class KnowledgeResponse(BaseModel):
    """知识库操作响应模型."""
    
    success: bool = Field(..., description='操作是否成功')
    message: str = Field(..., description='响应消息')
    doc_id: Optional[str] = Field(None, description='文档ID')
    data: Optional[Dict[str, Any]] = Field(None, description='额外数据')


class KnowledgeSearchResult(BaseModel):
    """知识库检索结果模型."""
    
    content: str = Field(..., description='知识内容')
    category: str = Field(..., description='知识分类')
    score: float = Field(..., description='相似度分数（0-1）')
    metadata: Dict[str, Any] = Field(default_factory=dict, description='元数据')
    
    model_config = {
        'json_schema_extra': {
            'example': {
                'content': '退货需在收货后7天内申请',
                'category': '售后政策',
                'score': 0.95,
                'metadata': {'source': '官网'},
            }
        }
    }


class KnowledgeDetail(BaseModel):
    """知识库详情模型（包含所有分块）."""
    
    doc_id: str = Field(..., description='文档ID')
    content: str = Field(..., description='知识内容（完整内容，合并所有分块）')
    category: str = Field(..., description='知识分类')
    title: Optional[str] = Field(None, description='知识标题')
    tags: Optional[List[str]] = Field(default_factory=list, description='标签列表')
    created_at: str = Field(..., description='创建时间')
    updated_at: Optional[str] = Field(None, description='更新时间')
    metadata: Dict[str, Any] = Field(default_factory=dict, description='元数据')
    chunks: List[Dict[str, Any]] = Field(default_factory=list, description='所有分块信息')


class PaginatedKnowledgeResponse(BaseModel):
    """分页知识库响应模型."""
    
    items: List[KnowledgeSearchResult] = Field(..., description='知识条目列表')
    total: int = Field(..., description='总数量')
    page: int = Field(..., description='当前页码')
    page_size: int = Field(..., description='每页数量')
    total_pages: int = Field(..., description='总页数')


class KnowledgeListResponse(BaseModel):
    """知识库列表响应模型."""
    
    total: int = Field(..., description='总数量')
    items: List[KnowledgeBase] = Field(..., description='知识条目列表')


class ImportErrorDetail(BaseModel):
    """导入错误详情."""
    
    row: int = Field(..., description='行号（从1开始）')
    error: str = Field(..., description='错误信息')


class ImportResult(BaseModel):
    """导入结果模型."""
    
    success_count: int = Field(..., description='成功导入数量')
    failed_count: int = Field(..., description='失败数量')
    total_count: int = Field(..., description='总数量')
    errors: List[ImportErrorDetail] = Field(default_factory=list, description='错误列表')
    preview: List[Dict[str, Any]] = Field(default_factory=list, description='预览数据（前5条）')

