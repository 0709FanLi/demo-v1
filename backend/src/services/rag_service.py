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
PROMPT_TEMPLATE = """你是一位资深的抗衰老领域专家。请严格遵守以下规则：

【角色定位】
- 你是一位在抗衰老、健康管理和长寿科学领域有多年研究和实践经验的专家
- 你精通细胞生物学、营养学、运动科学、再生医学等与抗衰老相关的专业知识
- 你的回答要基于科学证据和最新研究成果，专业、严谨、可信
- 你可以提供个性化的抗衰老建议，但要明确指出这不是医疗诊断，建议咨询专业医生

【知识库参考】
{knowledge_context}

【回答要求】
1. **必须优先基于【知识库参考】中的科学文献和专业资料回答**
2. 引用知识库内容时，要说明研究来源或科学依据
3. 如果知识库中没有相关信息，可以基于专业知识回答，但要明确说明"这是基于通用的抗衰老科学知识"
4. 回答要兼顾专业性和易理解性，适当使用类比和实例
5. 涉及具体的营养补充剂、药物或医疗方案时，务必提醒用户咨询专业医生
6. 如果用户问题不够具体，引导用户提供更多信息（如年龄、健康状况、生活方式等）

【用户问题】
{user_question}

【历史对话】
{history_context}

请以专家的角度回答用户问题，提供科学、实用的抗衰老建议。
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
            max_relevance_score = 0.0
            is_out_of_scope = False
            
            if request.use_knowledge_base:
                search_results = await self.knowledge_service.search_knowledge(
                    query=request.question,
                    top_k=settings.knowledge_top_k,
                )
                
                if search_results:
                    # 获取最高相似度
                    max_relevance_score = search_results[0].score
                    
                    # 判断是否超出知识库范围
                    if max_relevance_score < settings.knowledge_relevance_threshold:
                        is_out_of_scope = True
                        logger.info(
                            f'问题超出知识库范围 - 最高相似度: {max_relevance_score:.2f}, '
                            f'阈值: {settings.knowledge_relevance_threshold}'
                        )
                    else:
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
                            f'最高相似度: {max_relevance_score:.2f}'
                        )
                else:
                    # 没有检索结果，也视为超出范围
                    is_out_of_scope = True
                    logger.info('知识库检索无结果，视为超出范围')
            
            # 步骤2: 如果超出范围，直接返回友好提示
            if is_out_of_scope:
                out_of_scope_message = self._generate_out_of_scope_message(
                    question=request.question,
                    max_score=max_relevance_score,
                )
                
                return ChatResponse(
                    answer=out_of_scope_message,
                    confidence='低',
                    knowledge_sources=[],
                    llm_model='out_of_scope',
                    has_image=False,
                    out_of_scope=True,
                    relevance_score=max_relevance_score,
                )
            
            # 步骤3: 构建历史对话上下文
            history_context = '这是首次对话。'
            if request.history:
                history_parts = []
                for msg in request.history[-5:]:  # 只保留最近5轮
                    role_name = '用户' if msg.role == 'user' else '助手'
                    history_parts.append(f'{role_name}: {msg.content}')
                history_context = '\n'.join(history_parts)
            
            # 步骤4: 填充提示词模板
            full_prompt = PROMPT_TEMPLATE.format(
                knowledge_context=knowledge_context,
                user_question=request.question,
                history_context=history_context,
            )
            
            # 步骤5: 调用大模型
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
            
            # 步骤6: 评估置信度
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
                out_of_scope=False,
                relevance_score=max_relevance_score,
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
                out_of_scope=False,
                relevance_score=None,
            )
    
    def _generate_out_of_scope_message(
        self,
        question: str,
        max_score: float,
    ) -> str:
        """生成超出知识库范围的友好提示.
        
        Args:
            question: 用户问题
            max_score: 最高相似度分数
            
        Returns:
            友好的提示消息
        """
        message = f"""抱歉，您的问题似乎超出了我的专业知识库范围。

📚 **我的专业领域**
我目前专注于以下领域的专业咨询：
• 抗衰老科学与策略
• 健康管理与长寿研究  
• 细胞生物学与再生医学
• 营养学与运动科学
• 衰老相关的医学研究

💡 **建议您**
1. 咨询相关领域的专业医生或专家
2. 重新描述问题，看是否与抗衰老健康相关
3. 查看我的知识库涵盖范围

❓ **您的问题**: {question}

如果您认为这个问题应该属于我的专业范围，请尝试换个方式提问，或提供更多背景信息。

---
相关性评分: {max_score:.2f} / 阈值: {settings.knowledge_relevance_threshold}"""
        
        return message
    
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

