"""
加载示例知识库数据脚本

使用方法：
    python load_example_knowledge.py
"""

import json
import asyncio
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.services import KnowledgeService
from src.models.schemas import KnowledgeCreate
from src.utils import logger


async def load_knowledge_from_json(json_file: str = 'example_knowledge.json'):
    """从JSON文件加载知识库数据.
    
    Args:
        json_file: JSON文件路径
    """
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            knowledge_list = json.load(f)
        
        logger.info(f'读取到 {len(knowledge_list)} 条知识')
        
        # 初始化服务
        service = KnowledgeService()
        
        # 批量添加
        success_count = 0
        for idx, item in enumerate(knowledge_list, 1):
            try:
                knowledge = KnowledgeCreate(
                    content=item['content'],
                    category=item['category'],
                )
                
                doc_id = await service.add_knowledge(knowledge)
                logger.info(f'[{idx}/{len(knowledge_list)}] 添加成功 - {item["category"]}: {doc_id}')
                success_count += 1
                
            except Exception as e:
                logger.error(f'[{idx}/{len(knowledge_list)}] 添加失败: {e}')
        
        logger.info(f'✅ 完成！成功添加 {success_count}/{len(knowledge_list)} 条知识')
        
        # 显示统计
        total = await service.get_knowledge_count()
        logger.info(f'📊 当前知识库总数: {total} 条')
        
    except FileNotFoundError:
        logger.error(f'❌ 文件不存在: {json_file}')
    except json.JSONDecodeError:
        logger.error(f'❌ JSON格式错误: {json_file}')
    except Exception as e:
        logger.error(f'❌ 加载失败: {e}')


async def test_search():
    """测试知识检索."""
    service = KnowledgeService()
    
    test_queries = [
        '如何退货',
        '支付方式',
        '客服电话',
    ]
    
    logger.info('\n🔍 测试知识检索:')
    for query in test_queries:
        results = await service.search_knowledge(query, top_k=2)
        logger.info(f'\n查询: {query}')
        for i, result in enumerate(results, 1):
            logger.info(f'  [{i}] 相似度: {result.score:.3f} | {result.content[:50]}...')


if __name__ == '__main__':
    print('=' * 60)
    print('🚀 加载示例知识库数据')
    print('=' * 60)
    
    # 加载知识
    asyncio.run(load_knowledge_from_json())
    
    # 测试检索
    print('\n' + '=' * 60)
    asyncio.run(test_search())
    print('=' * 60)

