"""Pydantic schemas模块."""

from .knowledge import (
    KnowledgeBase,
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeSearchResult,
)
from .chat import (
    ChatRequest,
    ChatResponse,
    Message,
)

__all__ = [
    'KnowledgeBase',
    'KnowledgeCreate',
    'KnowledgeResponse',
    'KnowledgeSearchResult',
    'ChatRequest',
    'ChatResponse',
    'Message',
]

