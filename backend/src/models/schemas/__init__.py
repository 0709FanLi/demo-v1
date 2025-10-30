"""Pydantic schemas模块."""

from .knowledge import (
    KnowledgeBase,
    KnowledgeCreate,
    KnowledgeUpdate,
    KnowledgeResponse,
    KnowledgeSearchResult,
    KnowledgeDetail,
    PaginatedKnowledgeResponse,
    KnowledgeListResponse,
    ImportResult,
    ImportErrorDetail,
)
from .chat import (
    ChatRequest,
    ChatResponse,
    Message,
)

__all__ = [
    'KnowledgeBase',
    'KnowledgeCreate',
    'KnowledgeUpdate',
    'KnowledgeResponse',
    'KnowledgeSearchResult',
    'KnowledgeDetail',
    'PaginatedKnowledgeResponse',
    'KnowledgeListResponse',
    'ImportResult',
    'ImportErrorDetail',
    'ChatRequest',
    'ChatResponse',
    'Message',
]

