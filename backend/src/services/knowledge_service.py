"""知识库管理服务（基于 Milvus）.

负责知识库的增删改查和向量检索功能。
遵守企业级规范：
- 完整类型提示
- 异步操作
- 错误处理和日志
- 单一职责
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from sentence_transformers import SentenceTransformer

from ..config import settings
from ..models.schemas import KnowledgeCreate, KnowledgeSearchResult
from ..utils import logger, KnowledgeBaseError, VectorSearchError
from ..utils.helpers import generate_doc_id, split_text


class KnowledgeService:
    """知识库管理服务类（Milvus实现）.
    
    功能：
    1. 知识条目的增删改查
    2. 文本向量化
    3. 向量相似度检索
    4. 知识库持久化
    """
    
    def __init__(self):
        """初始化知识库服务.
        
        创建Milvus连接和加载向量化模型。
        """
        self._initialize_milvus()
        self._initialize_embedding_model()
        self._create_collection()
        logger.info('知识库服务初始化完成（Milvus）')
    
    def _initialize_milvus(self) -> None:
        """初始化Milvus连接."""
        try:
            connections.connect(
                alias='default',
                host=settings.milvus_host,
                port=str(settings.milvus_port),
            )
            logger.info(
                f'Milvus连接成功 - {settings.milvus_host}:{settings.milvus_port}'
            )
            
        except Exception as e:
            logger.error(f'Milvus连接失败: {e}')
            raise KnowledgeBaseError(f'Milvus连接失败: {str(e)}')
    
    def _initialize_embedding_model(self) -> None:
        """初始化文本向量化模型."""
        try:
            self.embedding_model = SentenceTransformer(
                settings.embedding_model
            )
            # 获取向量维度
            self.vector_dim = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(
                f'向量化模型加载成功: {settings.embedding_model}, '
                f'维度: {self.vector_dim}'
            )
            
        except Exception as e:
            logger.error(f'向量化模型加载失败: {e}')
            raise KnowledgeBaseError(f'模型加载失败: {str(e)}')
    
    def _create_collection(self) -> None:
        """创建或获取Milvus集合."""
        try:
            collection_name = 'knowledge_base'
            
            # 如果集合已存在，直接加载
            if utility.has_collection(collection_name):
                self.collection = Collection(collection_name)
                self.collection.load()
                logger.info(
                    f'加载现有集合: {collection_name}, '
                    f'文档数: {self.collection.num_entities}'
                )
                return
            
            # 定义字段
            fields = [
                FieldSchema(
                    name='id',
                    dtype=DataType.VARCHAR,
                    max_length=100,
                    is_primary=True,
                ),
                FieldSchema(
                    name='content',
                    dtype=DataType.VARCHAR,
                    max_length=65535,
                ),
                FieldSchema(
                    name='vector',
                    dtype=DataType.FLOAT_VECTOR,
                    dim=self.vector_dim,
                ),
                FieldSchema(
                    name='category',
                    dtype=DataType.VARCHAR,
                    max_length=100,
                ),
                FieldSchema(
                    name='created_at',
                    dtype=DataType.VARCHAR,
                    max_length=50,
                ),
                FieldSchema(
                    name='chunk_index',
                    dtype=DataType.INT64,
                ),
            ]
            
            # 创建schema
            schema = CollectionSchema(
                fields=fields,
                description='企业知识库（多模态支持）',
            )
            
            # 创建集合
            self.collection = Collection(
                name=collection_name,
                schema=schema,
            )
            
            # 创建索引
            index_params = {
                'metric_type': 'COSINE',  # 余弦相似度
                'index_type': 'IVF_FLAT',
                'params': {'nlist': 128},
            }
            self.collection.create_index(
                field_name='vector',
                index_params=index_params,
            )
            
            # 加载集合到内存
            self.collection.load()
            
            logger.info(f'创建新集合: {collection_name}')
            
        except Exception as e:
            logger.error(f'创建集合失败: {e}')
            raise KnowledgeBaseError(f'集合创建失败: {str(e)}')
    
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
            
            # 准备数据
            created_at = datetime.now().isoformat()
            
            ids = [f'{doc_id}_chunk_{i}' for i in range(len(chunks))]
            contents = chunks
            vectors = embeddings
            categories = [knowledge.category] * len(chunks)
            created_ats = [created_at] * len(chunks)
            chunk_indices = list(range(len(chunks)))
            
            # 插入数据
            entities = [
                ids,
                contents,
                vectors,
                categories,
                created_ats,
                chunk_indices,
            ]
            
            self.collection.insert(entities)
            self.collection.flush()
            
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
            
            # 构建过滤表达式
            expr = None
            if category:
                expr = f'category == "{category}"'
            
            # 搜索参数
            search_params = {
                'metric_type': 'COSINE',
                'params': {'nprobe': 10},
            }
            
            # 执行检索
            results = self.collection.search(
                data=[query_embedding],
                anns_field='vector',
                param=search_params,
                limit=top_k,
                expr=expr,
                output_fields=['content', 'category', 'created_at'],
            )
            
            # 解析结果
            search_results = []
            
            if results and len(results) > 0:
                for hit in results[0]:
                    # Milvus返回的距离是余弦距离，需要转换为相似度
                    # 余弦相似度 = 1 - 余弦距离
                    score = 1.0 - hit.distance
                    
                    # 获取entity数据
                    content = hit.entity.content if hasattr(hit.entity, 'content') else ''
                    category = hit.entity.category if hasattr(hit.entity, 'category') else '未分类'
                    created_at = hit.entity.created_at if hasattr(hit.entity, 'created_at') else ''
                    
                    search_results.append(
                        KnowledgeSearchResult(
                            content=content,
                            category=category,
                            score=round(max(0.0, score), 4),
                            metadata={
                                'created_at': created_at,
                                'id': hit.id,
                            },
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
            # 构建删除表达式（删除所有相关分块）
            expr = f'id like "{doc_id}%"'
            
            self.collection.delete(expr)
            self.collection.flush()
            
            logger.info(f'知识条目删除成功 - ID: {doc_id}')
            return True
            
        except Exception as e:
            logger.error(f'删除知识条目失败: {e}')
            raise KnowledgeBaseError(f'删除失败: {str(e)}')
    
    async def get_knowledge_count(self) -> int:
        """获取知识库条目总数（不包括分块）.
        
        Returns:
            条目数量（只计算 chunk_index == 0 的记录）
        """
        try:
            # 只统计第一个分块的数量，避免重复计数
            results = self.collection.query(
                expr='chunk_index == 0',
                output_fields=['id'],
                limit=10000,  # 设置一个足够大的限制
            )
            count = len(results)
            logger.info(f'知识库条目数: {count}（总分块数: {self.collection.num_entities}）')
            return count
        except Exception as e:
            logger.error(f'获取知识库数量失败: {e}')
            return 0
    
    async def get_all_knowledge(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[KnowledgeSearchResult]:
        """获取所有知识条目.
        
        Args:
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            知识条目列表
        """
        try:
            # 查询所有记录
            results = self.collection.query(
                expr='chunk_index == 0',  # 只获取第一个分块（避免重复）
                output_fields=['content', 'category', 'created_at', 'id'],
                limit=limit,
                offset=offset,
            )
            
            knowledge_list = []
            for result in results:
                knowledge_list.append(
                    KnowledgeSearchResult(
                        content=result.get('content', ''),
                        category=result.get('category', '未分类'),
                        score=1.0,  # 不是搜索结果，没有相似度
                        metadata={
                            'created_at': result.get('created_at', ''),
                            'id': result.get('id', ''),
                        },
                    )
                )
            
            logger.info(f'获取知识列表成功 - 返回: {len(knowledge_list)} 条')
            return knowledge_list
            
        except Exception as e:
            logger.error(f'获取知识列表失败: {e}')
            return []
    
    async def clear_all(self) -> bool:
        """清空知识库（谨慎使用）.
        
        Returns:
            是否清空成功
        """
        try:
            # 删除集合
            utility.drop_collection('knowledge_base')
            
            # 重新创建
            self._create_collection()
            
            logger.warning('知识库已清空')
            return True
            
        except Exception as e:
            logger.error(f'清空知识库失败: {e}')
            raise KnowledgeBaseError(f'清空失败: {str(e)}')
