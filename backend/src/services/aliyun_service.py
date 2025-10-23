"""阿里云通义千问大模型服务.

负责调用阿里云DashScope API。
遵守企业级规范：
- 异步调用
- 重试机制
- 错误处理
- 结构化日志
"""

from typing import List, Optional, Dict, Any

import dashscope
from dashscope import Generation, MultiModalConversation
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ..config import settings
from ..models.schemas import Message
from ..utils import logger, ModelInferenceError


class AliyunService:
    """阿里云大模型服务类.
    
    功能：
    1. 文本对话（通义千问）
    2. 多模态对话（图文）
    3. 流式响应（可选）
    4. 自动重试
    """
    
    def __init__(self):
        """初始化阿里云服务."""
        dashscope.api_key = settings.dashscope_api_key
        logger.info('阿里云服务初始化完成')
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """纯文本对话.
        
        Args:
            messages: 对话消息列表
            model: 模型名称（默认使用配置）
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型回复内容
            
        Raises:
            ModelInferenceError: 推理失败时抛出
        """
        try:
            # 转换消息格式
            formatted_messages = [
                {'role': msg.role, 'content': msg.content}
                for msg in messages
            ]
            
            # 调用API
            response = Generation.call(
                model=model or settings.default_llm_model,
                messages=formatted_messages,
                result_format='message',
                temperature=temperature or settings.temperature,
                max_tokens=max_tokens or settings.max_tokens,
            )
            
            # 检查响应
            if response.status_code != 200:
                raise ModelInferenceError(
                    f'API调用失败: {response.message}',
                    details={
                        'status_code': response.status_code,
                        'request_id': response.request_id,
                    },
                )
            
            # 提取回复
            answer = response.output.choices[0].message.content
            
            logger.info(
                f'模型调用成功 - 模型: {model or settings.default_llm_model}, '
                f'输入token: {response.usage.input_tokens}, '
                f'输出token: {response.usage.output_tokens}'
            )
            
            return answer
            
        except ModelInferenceError:
            raise
        except Exception as e:
            logger.error(f'模型调用失败: {e}')
            raise ModelInferenceError(
                f'调用失败: {str(e)}',
                details={'model': model or settings.default_llm_model},
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def chat_with_image(
        self,
        text: str,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        history: Optional[List[Message]] = None,
        model: Optional[str] = None,
    ) -> str:
        """图文多模态对话.
        
        Args:
            text: 文本内容
            image_url: 图片URL
            image_base64: 图片Base64编码
            history: 历史对话
            model: 模型名称
            
        Returns:
            模型回复内容
            
        Raises:
            ModelInferenceError: 推理失败时抛出
        """
        try:
            # 构建消息内容
            content_parts = [{'text': text}]
            
            # 添加图片
            if image_url:
                content_parts.append({'image': image_url})
            elif image_base64:
                content_parts.append({'image': f'data:image/jpeg;base64,{image_base64}'})
            
            # 构建消息
            messages = []
            
            # 添加历史对话
            if history:
                for msg in history:
                    messages.append({
                        'role': msg.role,
                        'content': [{'text': msg.content}],
                    })
            
            # 添加当前消息
            messages.append({
                'role': 'user',
                'content': content_parts,
            })
            
            # 调用多模态API
            response = MultiModalConversation.call(
                model=model or settings.default_vl_model,
                messages=messages,
            )
            
            # 检查响应
            if response.status_code != 200:
                raise ModelInferenceError(
                    f'多模态API调用失败: {response.message}',
                    details={
                        'status_code': response.status_code,
                        'request_id': response.request_id,
                    },
                )
            
            # 提取回复
            answer = response.output.choices[0].message.content[0]['text']
            
            logger.info(
                f'多模态对话成功 - 模型: {model or settings.default_vl_model}, '
                f'包含图片: {bool(image_url or image_base64)}'
            )
            
            return answer
            
        except ModelInferenceError:
            raise
        except Exception as e:
            logger.error(f'多模态对话失败: {e}')
            raise ModelInferenceError(
                f'多模态调用失败: {str(e)}',
                details={'has_image': bool(image_url or image_base64)},
            )
    
    async def test_connection(self) -> bool:
        """测试API连接.
        
        Returns:
            连接是否正常
        """
        try:
            test_message = Message(role='user', content='你好')
            await self.chat([test_message])
            logger.info('阿里云API连接测试成功')
            return True
        except Exception as e:
            logger.error(f'阿里云API连接测试失败: {e}')
            return False

