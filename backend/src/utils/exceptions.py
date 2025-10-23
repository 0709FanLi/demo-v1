"""自定义异常类模块.

遵守企业级规范：
- 继承基础Exception
- 提供清晰的错误信息
- 便于API层转换为HTTP响应
"""

from typing import Optional


class ApiError(Exception):
    """API通用错误基类.
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        details: 详细错误信息
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class KnowledgeBaseError(ApiError):
    """知识库操作错误.
    
    用于知识库增删改查失败的场景。
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=f'知识库错误: {message}',
            status_code=400,
            details=details,
        )


class ModelInferenceError(ApiError):
    """大模型推理错误.
    
    用于调用阿里云大模型失败的场景。
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=f'模型推理错误: {message}',
            status_code=500,
            details=details,
        )


class VectorSearchError(ApiError):
    """向量检索错误.
    
    用于向量数据库检索失败的场景。
    """
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=f'向量检索错误: {message}',
            status_code=500,
            details=details,
        )

