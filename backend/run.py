#!/usr/bin/env python3
"""
简单的Python启动脚本
如果bash脚本有问题，可以直接运行此脚本

使用方法：
    python run.py
    或
    python3 run.py
"""

import os
import sys
import subprocess

def main():
    print("🚀 启动RAG智能对话系统后端...")
    print()
    
    # 检查Python版本
    version = sys.version_info
    print(f"📌 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ 错误: 需要Python 3.9或更高版本")
        sys.exit(1)
    
    # 警告高版本Python
    if version.major == 3 and version.minor >= 13:
        print("⚠️  警告: Python 3.13+可能存在兼容性问题，建议使用3.9-3.12")
        print()
    
    # 检查是否在虚拟环境中
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if not in_venv:
        print("⚠️  提示: 未检测到虚拟环境，建议创建虚拟环境：")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print()
    
    # 检查依赖
    print("🔍 检查依赖...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'dashscope',
        'chromadb',
        'sentence_transformers',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (未安装)")
            missing_packages.append(package)
    
    print()
    
    if missing_packages:
        print("❌ 缺少依赖包，请先安装：")
        print(f"   pip install {' '.join(missing_packages)}")
        print()
        print("或安装全部依赖：")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # 创建数据目录
    os.makedirs('data/chroma_db', exist_ok=True)
    
    # 检查配置文件
    if not os.path.exists('env_template.txt'):
        print("⚠️  警告: 未找到 env_template.txt 配置文件")
        print()
    
    # 启动服务
    print("🚀 启动FastAPI服务...")
    print("📝 API文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print()
    print("⚠️  首次启动可能需要下载向量模型，请耐心等待...")
    print("⚠️  按 Ctrl+C 停止服务")
    print()
    print("=" * 60)
    print()
    
    try:
        # 启动uvicorn
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'src.main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
    except KeyboardInterrupt:
        print()
        print("👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

