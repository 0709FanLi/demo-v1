"""应用配置管理模块.

遵守企业级Python规范：
- 使用pydantic-settings从环境变量加载配置
- 不硬编码敏感信息
- 提供类型提示和默认值
"""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类.
    
    从环境变量或.env文件加载配置。
    所有配置项必须有类型提示。
    """
    
    # 阿里云配置
    dashscope_api_key: str
    
    # 应用配置
    app_name: str = 'AI-RAG-Service'
    app_version: str = '1.0.0'
    debug: bool = True
    
    # 服务器配置
    host: str = '0.0.0.0'
    port: int = 8000
    
    # 向量数据库配置（Milvus）
    milvus_host: str = 'localhost'
    milvus_port: int = 19530
    embedding_model: str = 'BAAI/bge-large-zh-v1.5'  # 中文检索优化模型
    
    # 大模型配置
    default_llm_model: str = 'qwen-max'
    default_vl_model: str = 'qwen-vl-max'
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # 知识库配置
    knowledge_top_k: int = 3
    chunk_size: int = 500
    chunk_overlap: int = 50
    knowledge_relevance_threshold: float = 0.60  # 知识库相似度阈值（0-1），低于此值视为超出范围
    
    model_config = SettingsConfigDict(
        # 配置加载优先级：环境变量 > env_file
        # 环境变量会覆盖文件中的值
        env_file='env_template.txt',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    


# 全局配置实例
settings = Settings()

