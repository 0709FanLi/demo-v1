"""加载抗衰老知识库示例数据.

使用方法：
    python load_anti_aging_knowledge.py
"""

import asyncio
import json
from pathlib import Path

from src.services.knowledge_service import KnowledgeService
from src.models.schemas import KnowledgeCreate
from src.utils import logger


async def load_knowledge():
    """加载知识库数据."""
    # 读取JSON文件
    json_file = Path(__file__).parent / 'anti_aging_knowledge_example.json'
    
    if not json_file.exists():
        logger.error(f'文件不存在: {json_file}')
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        knowledge_list = json.load(f)
    
    logger.info(f'读取到 {len(knowledge_list)} 条知识')
    
    # 初始化知识库服务
    knowledge_service = KnowledgeService()
    
    # 逐条添加知识
    success_count = 0
    failed_count = 0
    
    for idx, item in enumerate(knowledge_list, 1):
        try:
            knowledge = KnowledgeCreate(
                content=item['content'],
                category=item['category'],
                metadata=item.get('metadata', {}),
            )
            
            doc_id = await knowledge_service.add_knowledge(knowledge)
            
            logger.info(
                f'[{idx}/{len(knowledge_list)}] 添加成功 - '
                f'分类: {item["category"]}, ID: {doc_id}'
            )
            success_count += 1
            
        except Exception as e:
            logger.error(f'[{idx}/{len(knowledge_list)}] 添加失败: {e}')
            failed_count += 1
    
    # 统计结果
    total_count = await knowledge_service.get_knowledge_count()
    
    logger.info('=' * 60)
    logger.info('知识库加载完成!')
    logger.info(f'成功添加: {success_count} 条')
    logger.info(f'失败: {failed_count} 条')
    logger.info(f'当前知识库总数: {total_count} 条')
    logger.info('=' * 60)


if __name__ == '__main__':
    asyncio.run(load_knowledge())

