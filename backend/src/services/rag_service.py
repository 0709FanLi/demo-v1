"""RAG（检索增强生成）服务.

整合知识库检索和大模型推理。
遵守企业级规范：
- 结构化提示词模板
- 可配置的检索策略
- 完整的错误处理
"""

from typing import Optional, List, Literal

from ..config import settings
from ..models.schemas import ChatRequest, ChatResponse, Message
from ..utils import logger
from .knowledge_service import KnowledgeService
from .aliyun_service import AliyunService


# 结构化提示词模板
PROMPT_TEMPLATE = """你是一个专业、友好的智能助手。请严格遵守以下规则：

【角色定位】
- 你是企业的官方客服助手
- 回答要准确、专业、有礼貌
- 如果不确定，诚实告知用户

【知识库参考】
{knowledge_context}

【回答要求】
1. **必须优先基于【知识库参考】中的内容回答**
2. 如果知识库中没有相关信息，可以基于常识回答，但要说明"这不是官方信息"
3. 回答要简洁明了，避免冗长
4. 如果用户问题不清楚，引导用户补充信息

【用户问题】
{user_question}

【历史对话】
{history_context}

请直接回答用户问题，不要重复上述规则。
"""


class RAGService:
    """RAG服务类.
    
    核心功能：
    1. 检索相关知识
    2. 构建增强提示词
    3. 调用大模型
    4. 评估回答质量
    """
    
    def __init__(
        self,
        knowledge_service: Optional[KnowledgeService] = None,
        aliyun_service: Optional[AliyunService] = None,
    ):
        """初始化RAG服务.
        
        Args:
            knowledge_service: 知识库服务实例
            aliyun_service: 阿里云服务实例
        """
        self.knowledge_service = knowledge_service or KnowledgeService()
        self.aliyun_service = aliyun_service or AliyunService()
        logger.info('RAG服务初始化完成')
    
    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """RAG对话主方法.
        
        Args:
            request: 对话请求
            
        Returns:
            对话响应
        """
        try:
            # 步骤1: 检索知识库
            knowledge_sources = []
            knowledge_context = '暂无相关知识库信息。'
            
            if request.use_knowledge_base:
                search_results = await self.knowledge_service.search_knowledge(
                    query=request.question,
                    top_k=settings.knowledge_top_k,
                )
                
                if search_results:
                    knowledge_sources = [
                        f'{result.content[:100]}...' 
                        for result in search_results
                    ]
                    
                    knowledge_context = '\n\n'.join([
                        f'[知识{i+1}] (相似度: {result.score:.2f})\n{result.content}'
                        for i, result in enumerate(search_results)
                    ])
                    
                    logger.info(
                        f'检索到 {len(search_results)} 条相关知识, '
                        f'最高相似度: {search_results[0].score:.2f}'
                    )
            
            # 步骤2: 构建历史对话上下文
            history_context = '这是首次对话。'
            if request.history:
                history_parts = []
                for msg in request.history[-5:]:  # 只保留最近5轮
                    role_name = '用户' if msg.role == 'user' else '助手'
                    history_parts.append(f'{role_name}: {msg.content}')
                history_context = '\n'.join(history_parts)
            
            # 步骤3: 填充提示词模板
            full_prompt = PROMPT_TEMPLATE.format(
                knowledge_context=knowledge_context,
                user_question=request.question,
                history_context=history_context,
            )
            
            # 步骤4: 调用大模型
            has_image = bool(request.image_url or request.image_base64)
            
            if has_image:
                # 多模态对话
                answer = await self.aliyun_service.chat_with_image(
                    text=full_prompt,
                    image_url=request.image_url,
                    image_base64=request.image_base64,
                    history=None,  # 历史已经在prompt中
                )
                model_used = settings.default_vl_model
            else:
                # 纯文本对话
                messages = [Message(role='user', content=full_prompt)]
                answer = await self.aliyun_service.chat(messages)
                model_used = settings.default_llm_model
            
            # 步骤5: 评估置信度
            confidence = self._evaluate_confidence(
                answer=answer,
                knowledge_found=bool(knowledge_sources),
            )
            
            # 构建响应
            response = ChatResponse(
                answer=answer,
                confidence=confidence,
                knowledge_sources=knowledge_sources,
                llm_model=model_used,
                has_image=has_image,
            )
            
            logger.info(
                f'RAG对话完成 - 问题: {request.question[:50]}..., '
                f'置信度: {confidence}, 使用知识库: {request.use_knowledge_base}'
            )
            
            return response
            
        except Exception as e:
            logger.error(f'RAG对话失败: {e}')
            # 返回友好的错误响应
            return ChatResponse(
                answer=f'抱歉，处理您的问题时遇到了错误：{str(e)}',
                confidence='低',
                knowledge_sources=[],
                llm_model='error',
                has_image=False,
            )
    
    def _evaluate_confidence(
        self,
        answer: str,
        knowledge_found: bool,
    ) -> Literal['高', '中', '低']:
        """评估回答置信度.
        
        Args:
            answer: 模型回答
            knowledge_found: 是否找到相关知识
            
        Returns:
            置信度等级
        """
        # 简单的启发式规则
        if not knowledge_found:
            return '低'
        
        # 检查回答长度
        if len(answer) < 20:
            return '低'
        
        # 检查是否包含不确定词汇
        uncertain_words = ['可能', '也许', '大概', '不确定', '不太清楚']
        if any(word in answer for word in uncertain_words):
            return '中'
        
        return '高'
    
    async def chat_simple(
        self,
        question: str,
        use_knowledge: bool = True,
    ) -> str:
        """简化的对话接口.
        
        Args:
            question: 用户问题
            use_knowledge: 是否使用知识库
            
        Returns:
            回答内容
        """
        request = ChatRequest(
            question=question,
            use_knowledge_base=use_knowledge,
        )
        response = await self.chat(request)
        return response.answer

