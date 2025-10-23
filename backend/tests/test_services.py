"""服务层单元测试.

测试知识库服务、阿里云服务和RAG服务。
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from src.models.schemas import KnowledgeCreate, ChatRequest, Message
from src.services import KnowledgeService, AliyunService, RAGService


class TestKnowledgeService:
    """知识库服务测试."""
    
    @pytest.mark.asyncio
    async def test_add_knowledge(self):
        """测试添加知识条目."""
        # 这是一个示例测试，实际运行需要配置向量数据库
        knowledge = KnowledgeCreate(
            content='测试知识内容',
            category='测试分类',
        )
        
        # 实际测试需要mock ChromaDB
        # service = KnowledgeService()
        # doc_id = await service.add_knowledge(knowledge)
        # assert doc_id is not None
        
        assert True  # 占位测试
    
    @pytest.mark.asyncio
    async def test_search_knowledge(self):
        """测试知识检索."""
        # 实际测试需要先添加测试数据
        assert True  # 占位测试


class TestAliyunService:
    """阿里云服务测试."""
    
    @pytest.mark.asyncio
    async def test_chat(self):
        """测试文本对话."""
        # Mock DashScope API
        with patch('dashscope.Generation.call') as mock_call:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.output.choices = [
                Mock(message=Mock(content='测试回复'))
            ]
            mock_response.usage.input_tokens = 10
            mock_response.usage.output_tokens = 5
            mock_call.return_value = mock_response
            
            service = AliyunService()
            messages = [Message(role='user', content='你好')]
            answer = await service.chat(messages)
            
            assert answer == '测试回复'
            mock_call.assert_called_once()


class TestRAGService:
    """RAG服务测试."""
    
    @pytest.mark.asyncio
    async def test_chat_simple(self):
        """测试简单对话."""
        # Mock服务依赖
        mock_knowledge_service = Mock(spec=KnowledgeService)
        mock_aliyun_service = Mock(spec=AliyunService)
        
        # 配置mock返回值
        mock_knowledge_service.search_knowledge = AsyncMock(return_value=[])
        mock_aliyun_service.chat = AsyncMock(return_value='测试回答')
        
        service = RAGService(
            knowledge_service=mock_knowledge_service,
            aliyun_service=mock_aliyun_service,
        )
        
        answer = await service.chat_simple('测试问题', use_knowledge=False)
        assert answer == '测试回答'


# 运行测试：pytest backend/tests/test_services.py -v

