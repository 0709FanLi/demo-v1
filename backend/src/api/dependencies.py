"""FastAPI依赖注入模块.

提供全局依赖，如服务实例、数据库会话等。
遵守依赖注入原则，避免使用全局变量。
"""

from typing import Generator

from ..services import KnowledgeService, AliyunService, RAGService


# 服务实例缓存
_knowledge_service: KnowledgeService = None
_aliyun_service: AliyunService = None
_rag_service: RAGService = None


def get_knowledge_service() -> KnowledgeService:
    """获取知识库服务实例（单例）.
    
    Returns:
        知识库服务实例
    """
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service


def get_aliyun_service() -> AliyunService:
    """获取阿里云服务实例（单例）.
    
    Returns:
        阿里云服务实例
    """
    global _aliyun_service
    if _aliyun_service is None:
        _aliyun_service = AliyunService()
    return _aliyun_service


def get_rag_service() -> RAGService:
    """获取RAG服务实例（单例）.
    
    Returns:
        RAG服务实例
    """
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(
            knowledge_service=get_knowledge_service(),
            aliyun_service=get_aliyun_service(),
        )
    return _rag_service

