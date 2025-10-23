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


class KnowledgeListResponse(BaseModel):
    """知识库列表响应模型."""
    
    total: int = Field(..., description='总数量')
    items: List[KnowledgeBase] = Field(..., description='知识条目列表')

