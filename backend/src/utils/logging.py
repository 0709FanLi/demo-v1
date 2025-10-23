"""企业级日志配置模块.

遵守规范：
- 使用loguru替代标准logging
- 结构化日志输出
- 支持文件和控制台输出
- 日志轮转和保留策略
"""

import sys
from pathlib import Path

from loguru import logger

from ..config import settings


def setup_logging() -> None:
    """配置日志系统."""
    
    # 移除默认handler
    logger.remove()
    
    # 控制台输出
    log_format = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | '
        '<level>{message}</level>'
    )
    
    logger.add(
        sys.stdout,
        format=log_format,
        level='DEBUG' if settings.debug else 'INFO',
        colorize=True,
    )
    
    # 文件输出（带轮转）
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / 'app_{time:YYYY-MM-DD}.log',
        format=log_format,
        level='INFO',
        rotation='00:00',  # 每天午夜轮转
        retention='30 days',  # 保留30天
        compression='zip',  # 压缩旧日志
        encoding='utf-8',
    )
    
    # 错误日志单独文件
    logger.add(
        log_dir / 'error_{time:YYYY-MM-DD}.log',
        format=log_format,
        level='ERROR',
        rotation='00:00',
        retention='90 days',  # 错误日志保留更久
        compression='zip',
        encoding='utf-8',
    )
    
    logger.info(f'日志系统初始化完成 - 应用: {settings.app_name} v{settings.app_version}')


# 初始化日志
setup_logging()

__all__ = ['logger']

