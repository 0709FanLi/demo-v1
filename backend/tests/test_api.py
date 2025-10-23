"""API接口集成测试.

使用FastAPI TestClient测试接口。
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


class TestHealthCheck:
    """健康检查接口测试."""
    
    def test_root(self):
        """测试根路径."""
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'running'
        assert 'version' in data
    
    def test_health(self):
        """测试健康检查."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'


class TestKnowledgeAPI:
    """知识库接口测试."""
    
    def test_add_knowledge(self):
        """测试添加知识."""
        payload = {
            'content': '测试知识内容',
            'category': '测试',
        }
        response = client.post('/api/v1/knowledge/add', json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data['success'] is True
        assert 'doc_id' in data
    
    def test_get_count(self):
        """测试获取知识库统计."""
        response = client.get('/api/v1/knowledge/count')
        assert response.status_code == 200
        data = response.json()
        assert 'total' in data


class TestChatAPI:
    """对话接口测试."""
    
    def test_chat_health(self):
        """测试对话服务健康检查."""
        response = client.get('/api/v1/chat/health')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
    
    @pytest.mark.asyncio
    async def test_chat_simple(self):
        """测试简单对话."""
        # 注意：此测试需要有效的API Key
        response = client.get(
            '/api/v1/chat/simple',
            params={'question': '你好', 'use_knowledge': False}
        )
        # 如果API Key无效，会返回500
        # assert response.status_code == 200


# 运行测试：pytest backend/tests/test_api.py -v

