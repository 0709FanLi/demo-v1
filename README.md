# 🧬 抗衰老专家咨询系统

基于阿里云通义千问大模型和 Milvus 向量数据库的**抗衰老领域专家咨询系统**，采用 RAG（检索增强生成）技术，提供科学、专业的抗衰老建议和健康管理方案。

## ⚡ 快速开始

### 一键启动（推荐）⭐

```bash
bash 启动服务.sh
```

自动启动 Milvus + 后端 + 前端，访问：
- 前端应用: http://localhost:3000
- API文档: http://localhost:8001/docs
- Milvus: http://localhost:19530

### 停止服务

```bash
bash 停止服务.sh
```

## ✨ 核心功能

- 🧬 **抗衰老专家定位**：提供基于科学证据的专业建议
- 📚 **专业知识库**：整合抗衰老领域的科学文献和临床研究
- 🔍 **智能语义检索**：使用 Milvus 向量数据库快速匹配相关知识
- 💬 **RAG 智能对话**：检索增强生成，回答更准确、更专业
- 🖼️ **多模态输入**：支持文本和图片（如检查报告、身体指标）
- 🎯 **专家级提示词**：确保回答专业、严谨、易理解
- 📱 **响应式界面**：React 实现的现代化移动端优化 UI
- 🐳 **Docker 部署**：容器化部署，易于扩展和维护

## 📖 详细文档

查看 [项目详细说明.md](./项目详细说明.md) 了解：
- 技术架构详解
- 大模型调用逻辑
- RAG实现原理
- 数据库设计
- API接口说明

## 🏗️ 技术架构

### 后端技术栈
- **FastAPI**: 高性能异步Web框架
- **Milvus 2.4**: 企业级向量数据库
- **PyMilvus**: Milvus Python SDK
- **Sentence-Transformers**: 文本向量化（384维）
- **DashScope**: 阿里云通义千问SDK
- **Pydantic**: 数据验证和配置管理
- **Loguru**: 企业级结构化日志
- **Docker**: 容器化部署

### 前端技术栈
- **React 18**: 现代化前端框架
- **TypeScript**: 类型安全
- **Axios**: HTTP客户端
- **CSS3**: 响应式设计

## 📦 项目结构

```
demo-v1/
├── backend/                    # 后端服务
│   ├── src/
│   │   ├── api/               # API路由层
│   │   │   └── routers/
│   │   │       ├── knowledge.py  # 知识库管理
│   │   │       └── chat.py       # RAG对话
│   │   ├── services/          # 服务层
│   │   │   ├── knowledge_service.py  # 知识库服务
│   │   │   ├── aliyun_service.py     # 阿里云服务
│   │   │   └── rag_service.py        # RAG服务
│   │   ├── models/            # 数据模型
│   │   │   └── schemas/
│   │   ├── utils/             # 工具模块
│   │   ├── config/            # 配置管理
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试用例
│   ├── requirements.txt       # Python依赖
│   └── env_template.txt       # 环境变量模板
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── services/          # API服务
│   │   ├── types/             # TypeScript类型
│   │   ├── styles/            # 样式文件
│   │   └── App.tsx            # 主组件
│   └── package.json           # Node依赖
└── docs/                       # 文档目录
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- 阿里云通义千问API Key

### 1. 后端部署

#### 步骤1：安装Python依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2：配置环境变量

复制 `env_template.txt` 内容并创建环境配置（根据你的系统手动创建 .env 文件）：

```bash
# 环境变量配置
DASHSCOPE_API_KEY=your-api-key-here
APP_NAME=AI-RAG-Service
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

#### 步骤3：启动后端服务

```bash
# 方式1：直接运行
python -m src.main

# 方式2：使用uvicorn（推荐）
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# 启动成功后访问：
# - API文档: http://localhost:8000/docs
# - 接口测试: http://localhost:8000/redoc
```

### 2. 前端部署

#### 步骤1：安装Node依赖

```bash
cd frontend

# 安装依赖
npm install
# 或
yarn install
```

#### 步骤2：配置API地址

创建 `.env` 文件（或使用 env_config.txt）：

```bash
REACT_APP_API_URL=http://localhost:8000
```

#### 步骤3：启动前端应用

```bash
# 开发模式
npm start

# 访问地址：http://localhost:3000
```

## 📚 使用指南

### 1. 添加知识到知识库

#### 方式A：通过Web界面
1. 打开前端应用
2. 点击右上角"➕ 添加知识"按钮
3. 填写知识分类和内容
4. 点击"添加知识"

#### 方式B：通过API接口

```bash
# 添加单条知识
curl -X POST "http://localhost:8000/api/v1/knowledge/add" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "我们的产品支持7天无理由退货",
    "category": "售后政策"
  }'

# 批量添加知识
curl -X POST "http://localhost:8000/api/v1/knowledge/add-batch" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "content": "工作时间：周一至周五 9:00-18:00",
      "category": "客服信息"
    },
    {
      "content": "支持微信、支付宝、银行卡支付",
      "category": "支付方式"
    }
  ]'
```

### 2. RAG对话测试

#### 纯文本对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "如何申请退货？",
    "use_knowledge_base": true
  }'
```

#### 图文对话

```bash
curl -X POST "http://localhost:8000/api/v1/chat/with-image" \
  -F "question=这是什么产品？" \
  -F "image=@/path/to/image.jpg" \
  -F "use_knowledge_base=true"
```

### 3. 知识库管理

```bash
# 检索知识
curl "http://localhost:8000/api/v1/knowledge/search?query=退货&top_k=3"

# 获取知识库统计
curl "http://localhost:8000/api/v1/knowledge/count"

# 删除知识（需要doc_id）
curl -X DELETE "http://localhost:8000/api/v1/knowledge/delete/{doc_id}"

# 清空知识库（危险操作）
curl -X DELETE "http://localhost:8000/api/v1/knowledge/clear?confirm=true"
```

## 🧪 运行测试

```bash
cd backend

# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_services.py -v
pytest tests/test_api.py -v

# 查看测试覆盖率
pytest tests/ --cov=src --cov-report=html
```

## 📖 API文档

启动后端服务后，访问以下地址查看完整API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/chat/` | POST | RAG智能对话 |
| `/api/v1/chat/with-image` | POST | 图文对话 |
| `/api/v1/knowledge/add` | POST | 添加知识 |
| `/api/v1/knowledge/search` | GET | 检索知识 |
| `/api/v1/knowledge/count` | GET | 知识库统计 |
| `/health` | GET | 健康检查 |

## ⚙️ 配置说明

### 后端配置（env_template.txt）

```bash
# 阿里云API Key（必填）
DASHSCOPE_API_KEY=your-api-key

# 应用配置
APP_NAME=AI-RAG-Service
DEBUG=True

# 服务器配置
HOST=0.0.0.0
PORT=8000

# 向量数据库配置
VECTOR_DB_PATH=./data/chroma_db
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2

# 大模型配置
DEFAULT_LLM_MODEL=qwen-max         # 文本模型
DEFAULT_VL_MODEL=qwen-vl-max       # 多模态模型
MAX_TOKENS=2000
TEMPERATURE=0.7

# 知识库配置
KNOWLEDGE_TOP_K=3                  # 检索返回结果数
CHUNK_SIZE=500                     # 文本分块大小
CHUNK_OVERLAP=50                   # 分块重叠
```

### 前端配置（env_config.txt）

```bash
REACT_APP_API_URL=http://localhost:8000
```

## 🎨 前端功能

### 对话功能
- ✅ 实时消息流
- ✅ 图片上传预览
- ✅ 历史对话上下文
- ✅ 置信度显示
- ✅ 知识来源引用

### 知识库管理
- ✅ 添加知识条目
- ✅ 分类管理
- ✅ 实时统计

### UI特性
- ✅ 响应式设计
- ✅ 移动端优化
- ✅ 现代化渐变背景
- ✅ 流畅动画效果

## 🔧 故障排查

### 后端启动失败

1. **向量数据库错误**
   ```bash
   # 删除数据库重新初始化
   rm -rf backend/data/chroma_db
   ```

2. **API Key无效**
   - 检查 `env_template.txt` 中的 `DASHSCOPE_API_KEY`
   - 确认API Key有效且有额度

3. **端口占用**
   ```bash
   # 修改PORT配置或杀掉占用进程
   lsof -ti:8000 | xargs kill -9
   ```

### 前端连接失败

1. **CORS错误**
   - 确认后端CORS配置正确
   - 检查 `REACT_APP_API_URL` 配置

2. **网络错误**
   - 确认后端服务已启动
   - 检查防火墙设置

## 📝 开发指南

### 添加新的知识分类

编辑提示词模板：`backend/src/services/rag_service.py`

### 自定义向量模型

修改配置：`backend/env_template.txt` 中的 `EMBEDDING_MODEL`

支持的模型：
- `paraphrase-multilingual-MiniLM-L12-v2` (多语言)
- `sentence-transformers/all-MiniLM-L6-v2` (英文)
- `shibing624/text2vec-base-chinese` (中文)

### 更换大模型

修改配置中的 `DEFAULT_LLM_MODEL`，支持：
- `qwen-max` (最强性能)
- `qwen-plus` (平衡)
- `qwen-turbo` (高性价比)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 阿里云通义千问
- ChromaDB
- FastAPI
- React

---

**作者**: demo-v1 项目团队  
**更新时间**: 2024-01-01  
**版本**: 1.0.0
