"""对话相关的Pydantic模型.

用于RAG对话接口的请求和响应。
"""

from typing import Optional, List, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """消息模型."""
    
    role: Literal['user', 'assistant', 'system'] = Field(
        ...,
        description='消息角色',
    )
    content: str = Field(..., description='消息内容')


class ChatRequest(BaseModel):
    """RAG对话请求模型.
    
    Args:
        question: 用户问题
        image_url: 图片URL（可选）
        image_base64: 图片Base64编码（可选）
        use_knowledge_base: 是否使用知识库
        history: 历史对话（可选）
    """
    
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description='用户问题',
    )
    image_url: Optional[str] = Field(
        None,
        description='图片URL',
    )
    image_base64: Optional[str] = Field(
        None,
        description='图片Base64编码',
    )
    use_knowledge_base: bool = Field(
        default=True,
        description='是否使用知识库检索',
    )
    history: Optional[List[Message]] = Field(
        default=None,
        description='历史对话',
    )
    
    model_config = {
        'json_schema_extra': {
            'example': {
                'question': '如何申请退货？',
                'use_knowledge_base': True,
                'history': [
                    {'role': 'user', 'content': '你好'},
                    {'role': 'assistant', 'content': '您好，有什么可以帮您？'},
                ],
            }
        }
    }


class ChatResponse(BaseModel):
    """RAG对话响应模型.
    
    包含答案、置信度、引用来源等信息。
    """
    
    answer: str = Field(..., description='AI回答')
    confidence: Literal['高', '中', '低'] = Field(
        default='中',
        description='回答置信度',
    )
    knowledge_sources: List[str] = Field(
        default_factory=list,
        description='引用的知识库来源',
    )
    llm_model: str = Field(..., description='使用的模型')
    has_image: bool = Field(default=False, description='是否包含图片')
    out_of_scope: bool = Field(
        default=False,
        description='问题是否超出知识库范围',
    )
    relevance_score: Optional[float] = Field(
        default=None,
        description='知识库相关性评分（0-1）',
    )
    
    model_config = {
        'protected_namespaces': (),  # 允许model_开头的字段
        'json_schema_extra': {
            'example': {
                'answer': '您可以在收货后7天内申请退货，联系客服即可办理。',
                'confidence': '高',
                'knowledge_sources': [
                    '我们的产品支持7天无理由退货',
                    '退货需在收货后7天内申请',
                ],
                'llm_model': 'qwen-max',
                'has_image': False,
            }
        }
    }

