"""知识库管理服务.

负责知识库的增删改查和向量检索功能。
遵守企业级规范：
- 完整类型提示
- 异步操作
- 错误处理和日志
- 单一职责
"""

import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from ..config import settings
from ..models.schemas import KnowledgeCreate, KnowledgeSearchResult
from ..utils import logger, KnowledgeBaseError, VectorSearchError
from ..utils.helpers import generate_doc_id, split_text


class KnowledgeService:
    """知识库管理服务类.
    
    功能：
    1. 知识条目的增删改查
    2. 文本向量化
    3. 向量相似度检索
    4. 知识库持久化
    """
    
    def __init__(self):
        """初始化知识库服务.
        
        创建向量数据库连接和加载向量化模型。
        """
        self._initialize_vector_db()
        self._initialize_embedding_model()
        logger.info('知识库服务初始化完成')
    
    def _initialize_vector_db(self) -> None:
        """初始化Chroma向量数据库."""
        try:
            # 确保数据目录存在
            db_path = Path(settings.vector_db_path)
            db_path.mkdir(parents=True, exist_ok=True)
            
            # 创建Chroma客户端
            self.client = chromadb.Client(
                ChromaSettings(
                    persist_directory=str(db_path),
                    anonymized_telemetry=False,
                )
            )
            
            # 获取或创建集合
            self.collection = self.client.get_or_create_collection(
                name='knowledge_base',
                metadata={'description': '企业知识库'},
            )
            
            logger.info(
                f'向量数据库初始化成功 - 路径: {db_path}, '
                f'现有文档数: {self.collection.count()}'
            )
            
        except Exception as e:
            logger.error(f'向量数据库初始化失败: {e}')
            raise KnowledgeBaseError(f'数据库初始化失败: {str(e)}')
    
    def _initialize_embedding_model(self) -> None:
        """初始化文本向量化模型."""
        try:
            self.embedding_model = SentenceTransformer(
                settings.embedding_model
            )
            logger.info(f'向量化模型加载成功: {settings.embedding_model}')
            
        except Exception as e:
            logger.error(f'向量化模型加载失败: {e}')
            raise KnowledgeBaseError(f'模型加载失败: {str(e)}')
    
    async def add_knowledge(
        self,
        knowledge: KnowledgeCreate,
    ) -> str:
        """添加知识条目到向量库.
        
        Args:
            knowledge: 知识条目数据
            
        Returns:
            文档ID
            
        Raises:
            KnowledgeBaseError: 添加失败时抛出
        """
        try:
            # 生成文档ID
            doc_id = generate_doc_id(knowledge.content)
            
            # 检查是否已存在
            existing = self.collection.get(ids=[doc_id])
            if existing['ids']:
                logger.warning(f'文档已存在: {doc_id}')
                return doc_id
            
            # 文本分块（如果内容过长）
            chunks = split_text(
                knowledge.content,
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
            )
            
            # 向量化
            embeddings = self.embedding_model.encode(
                chunks,
                show_progress_bar=False,
            ).tolist()
            
            # 准备元数据
            metadata = {
                'category': knowledge.category,
                'created_at': datetime.now().isoformat(),
                'chunk_count': len(chunks),
                **(knowledge.metadata or {}),
            }
            
            # 存入向量库
            chunk_ids = [
                f'{doc_id}_chunk_{i}' for i in range(len(chunks))
            ]
            
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=[metadata] * len(chunks),
            )
            
            logger.info(
                f'知识条目添加成功 - ID: {doc_id}, '
                f'分块数: {len(chunks)}, 类别: {knowledge.category}'
            )
            
            return doc_id
            
        except Exception as e:
            logger.error(f'添加知识条目失败: {e}')
            raise KnowledgeBaseError(
                f'添加失败: {str(e)}',
                details={'content_length': len(knowledge.content)},
            )
    
    async def search_knowledge(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None,
    ) -> List[KnowledgeSearchResult]:
        """检索相关知识.
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            category: 过滤分类（可选）
            
        Returns:
            检索结果列表
            
        Raises:
            VectorSearchError: 检索失败时抛出
        """
        try:
            # 向量化查询
            query_embedding = self.embedding_model.encode(
                query,
                show_progress_bar=False,
            ).tolist()
            
            # 构建过滤条件
            where_filter = None
            if category:
                where_filter = {'category': category}
            
            # 执行检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
            )
            
            # 解析结果
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # 距离转换为相似度分数（0-1）
                    score = max(0.0, 1.0 - distance)
                    
                    search_results.append(
                        KnowledgeSearchResult(
                            content=content,
                            category=metadata.get('category', '未分类'),
                            score=round(score, 4),
                            metadata=metadata,
                        )
                    )
            
            logger.info(
                f'知识检索完成 - 查询: {query[:50]}..., '
                f'返回结果: {len(search_results)}'
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f'知识检索失败: {e}')
            raise VectorSearchError(
                f'检索失败: {str(e)}',
                details={'query': query},
            )
    
    async def delete_knowledge(self, doc_id: str) -> bool:
        """删除知识条目.
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            # 查找所有相关分块
            all_docs = self.collection.get()
            chunk_ids = [
                id for id in all_docs['ids']
                if id.startswith(doc_id)
            ]
            
            if not chunk_ids:
                logger.warning(f'文档不存在: {doc_id}')
                return False
            
            # 删除所有分块
            self.collection.delete(ids=chunk_ids)
            
            logger.info(f'知识条目删除成功 - ID: {doc_id}, 删除分块: {len(chunk_ids)}')
            return True
            
        except Exception as e:
            logger.error(f'删除知识条目失败: {e}')
            raise KnowledgeBaseError(f'删除失败: {str(e)}')
    
    async def get_knowledge_count(self) -> int:
        """获取知识库条目总数.
        
        Returns:
            条目数量
        """
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f'获取知识库数量失败: {e}')
            return 0
    
    async def clear_all(self) -> bool:
        """清空知识库（谨慎使用）.
        
        Returns:
            是否清空成功
        """
        try:
            # 删除集合
            self.client.delete_collection(name='knowledge_base')
            
            # 重新创建
            self.collection = self.client.get_or_create_collection(
                name='knowledge_base',
                metadata={'description': '企业知识库'},
            )
            
            logger.warning('知识库已清空')
            return True
            
        except Exception as e:
            logger.error(f'清空知识库失败: {e}')
            raise KnowledgeBaseError(f'清空失败: {str(e)}')

