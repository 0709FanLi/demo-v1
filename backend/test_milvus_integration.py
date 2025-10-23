"""Milvus集成测试脚本"""

import asyncio
import sys
from src.services.knowledge_service import KnowledgeService
from src.services.rag_service import RAGService
from src.models.schemas import KnowledgeCreate, ChatRequest

async def test_knowledge_service():
    """测试知识库服务"""
    print("\n=== 测试知识库服务 ===")
    
    service = KnowledgeService()
    
    # 1. 添加知识
    print("\n1. 添加知识...")
    knowledge1 = KnowledgeCreate(
        content="我们提供7天无理由退货服务，退货需在收货后7天内申请。",
        category="售后服务"
    )
    doc_id1 = await service.add_knowledge(knowledge1)
    print(f"   ✅ 添加成功: {doc_id1}")
    
    knowledge2 = KnowledgeCreate(
        content="我们提供24小时在线客服支持，随时为您解答问题。",
        category="客户服务"
    )
    doc_id2 = await service.add_knowledge(knowledge2)
    print(f"   ✅ 添加成功: {doc_id2}")
    
    knowledge3 = KnowledgeCreate(
        content="产品保修期为1年，保修期内免费维修。",
        category="售后服务"
    )
    doc_id3 = await service.add_knowledge(knowledge3)
    print(f"   ✅ 添加成功: {doc_id3}")
    
    # 2. 查询数量
    count = await service.get_knowledge_count()
    print(f"\n2. 知识库总数: {count}")
    
    # 3. 检索测试
    print("\n3. 检索测试...")
    queries = [
        "如何退货",
        "客服联系方式",
        "保修多久",
    ]
    
    for query in queries:
        results = await service.search_knowledge(query, top_k=2)
        print(f"\n   查询: {query}")
        for i, result in enumerate(results, 1):
            print(f"   结果{i}: {result.content[:40]}... (相似度: {result.score})")
    
    print("\n✅ 知识库服务测试通过")
    return service

async def test_rag_service(knowledge_service):
    """测试RAG服务"""
    print("\n\n=== 测试RAG服务 ===")
    
    rag_service = RAGService(knowledge_service=knowledge_service)
    
    # 测试对话
    print("\n1. 测试RAG对话...")
    request = ChatRequest(
        question="我想退货，怎么办理？",
        use_knowledge_base=True,
        history=[],
    )
    
    response = await rag_service.chat(request)
    print(f"\n   问题: {request.question}")
    print(f"   回答: {response.answer[:200]}...")
    print(f"   置信度: {response.confidence}")
    print(f"   知识来源数: {len(response.knowledge_sources)}")
    print(f"   使用模型: {response.llm_model}")
    
    print("\n✅ RAG服务测试通过")

async def main():
    """主测试函数"""
    try:
        print("=" * 60)
        print("Milvus 集成测试")
        print("=" * 60)
        
        # 测试知识库服务
        knowledge_service = await test_knowledge_service()
        
        # 测试RAG服务
        await test_rag_service(knowledge_service)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

