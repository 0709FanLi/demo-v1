"""FastAPI应用主入口.

应用启动和配置，路由注册，中间件配置。
遵守企业级规范：
- 清晰的应用结构
- CORS配置
- 错误处理
- API文档配置
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .utils import logger, ApiError
from .api.routers import knowledge, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理.
    
    启动和关闭时的清理工作。
    """
    # 启动时
    logger.info(f'应用启动 - {settings.app_name} v{settings.app_version}')
    logger.info(f'Debug模式: {settings.debug}')
    logger.info(f'Milvus地址: {settings.milvus_host}:{settings.milvus_port}')
    
    yield
    
    # 关闭时
    logger.info('应用关闭')


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='基于阿里云通义千问的RAG智能对话系统',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)


# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# 全局异常处理
@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    """处理自定义API错误.
    
    Args:
        request: 请求对象
        exc: API错误
        
    Returns:
        JSON错误响应
    """
    logger.error(
        f'API错误 - 路径: {request.url.path}, '
        f'错误: {exc.message}, 状态码: {exc.status_code}'
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'error': exc.message,
            'details': exc.details,
            'status_code': exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理未捕获的异常.
    
    Args:
        request: 请求对象
        exc: 异常
        
    Returns:
        JSON错误响应
    """
    logger.error(f'未处理异常 - 路径: {request.url.path}, 错误: {exc}')
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': '服务器内部错误',
            'details': str(exc) if settings.debug else '请联系管理员',
            'status_code': 500,
        },
    )


# 注册路由
app.include_router(knowledge.router)
app.include_router(chat.router)


# 根路径
@app.get('/', tags=['系统'])
async def root() -> dict:
    """根路径，返回应用信息.
    
    Returns:
        应用信息
    """
    return {
        'name': settings.app_name,
        'version': settings.app_version,
        'status': 'running',
        'docs': '/docs',
        'message': '欢迎使用RAG智能对话系统',
    }


# 健康检查
@app.get('/health', tags=['系统'])
async def health_check() -> dict:
    """健康检查接口.
    
    Returns:
        健康状态
    """
    return {
        'status': 'healthy',
        'service': settings.app_name,
        'version': settings.app_version,
    }


if __name__ == '__main__':
    import uvicorn
    
    uvicorn.run(
        'main:app',
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level='info',
    )

