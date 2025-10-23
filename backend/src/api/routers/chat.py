"""RAG对话API路由.

提供基于知识库的智能对话接口，支持图文输入。
"""

from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    File,
    UploadFile,
    Form,
)

from ...models.schemas import ChatRequest, ChatResponse
from ...services import RAGService
from ...utils import logger
from ...utils.helpers import resize_image, image_to_base64
from ..dependencies import get_rag_service


router = APIRouter(
    prefix='/api/v1/chat',
    tags=['RAG对话'],
)


@router.post(
    '/',
    response_model=ChatResponse,
    summary='RAG智能对话',
    description='基于知识库的智能对话，支持图文输入和历史上下文',
)
async def chat(
    request: ChatRequest,
    service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """RAG对话接口.
    
    Args:
        request: 对话请求
        service: RAG服务（依赖注入）
        
    Returns:
        对话响应
    """
    try:
        response = await service.chat(request)
        return response
        
    except Exception as e:
        logger.error(f'对话处理失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'对话失败: {str(e)}',
        )


@router.post(
    '/with-image',
    response_model=ChatResponse,
    summary='图文对话',
    description='支持上传图片的对话接口（multipart/form-data）',
)
async def chat_with_image(
    question: str = Form(..., description='用户问题'),
    image: Optional[UploadFile] = File(None, description='图片文件'),
    use_knowledge_base: bool = Form(True, description='是否使用知识库'),
    service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """图文对话接口（文件上传形式）.
    
    Args:
        question: 用户问题
        image: 图片文件
        use_knowledge_base: 是否使用知识库
        service: RAG服务
        
    Returns:
        对话响应
    """
    try:
        image_base64 = None
        
        # 处理图片上传
        if image:
            # 读取图片数据
            image_bytes = await image.read()
            
            # 压缩图片
            resized_image = resize_image(image_bytes, max_size=1024)
            
            # 转换为Base64
            image_base64 = image_to_base64(resized_image)
            
            logger.info(
                f'图片上传成功 - 文件名: {image.filename}, '
                f'原始大小: {len(image_bytes)} bytes, '
                f'压缩后: {len(resized_image)} bytes'
            )
        
        # 构建请求
        request = ChatRequest(
            question=question,
            image_base64=image_base64,
            use_knowledge_base=use_knowledge_base,
        )
        
        # 调用RAG服务
        response = await service.chat(request)
        return response
        
    except Exception as e:
        logger.error(f'图文对话失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'图文对话失败: {str(e)}',
        )


@router.get(
    '/simple',
    response_model=dict,
    summary='简单对话',
    description='简化的对话接口，只需传入问题文本',
)
async def chat_simple(
    question: str,
    use_knowledge: bool = True,
    service: RAGService = Depends(get_rag_service),
) -> dict:
    """简单对话接口.
    
    Args:
        question: 用户问题
        use_knowledge: 是否使用知识库
        service: RAG服务
        
    Returns:
        简单响应
    """
    try:
        answer = await service.chat_simple(question, use_knowledge)
        return {
            'question': question,
            'answer': answer,
        }
        
    except Exception as e:
        logger.error(f'简单对话失败: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'对话失败: {str(e)}',
        )


@router.get(
    '/health',
    summary='健康检查',
    description='检查对话服务是否正常',
)
async def health_check() -> dict:
    """健康检查接口.
    
    Returns:
        服务状态
    """
    return {
        'status': 'healthy',
        'service': 'RAG Chat Service',
        'message': '服务运行正常',
    }

