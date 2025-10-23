# 📡 API接口文档

完整的RESTful API接口说明。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **文档地址**: 
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

### 错误响应
```json
{
  "error": "错误描述",
  "details": {},
  "status_code": 400
}
```

---

## 1. 系统接口

### 1.1 根路径
**GET** `/`

获取应用基本信息。

**响应示例**:
```json
{
  "name": "AI-RAG-Service",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "message": "欢迎使用RAG智能对话系统"
}
```

### 1.2 健康检查
**GET** `/health`

检查服务健康状态。

**响应示例**:
```json
{
  "status": "healthy",
  "service": "AI-RAG-Service",
  "version": "1.0.0"
}
```

---

## 2. 知识库管理接口

### 2.1 添加知识条目
**POST** `/api/v1/knowledge/add`

向知识库添加单条知识。

**请求体**:
```json
{
  "content": "我们的产品支持7天无理由退货",
  "category": "售后政策",
  "metadata": {
    "source": "官网",
    "version": "1.0"
  }
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | ✅ | 知识内容 (1-10000字符) |
| category | string | ❌ | 知识分类 (默认"通用") |
| metadata | object | ❌ | 自定义元数据 |

**响应示例**:
```json
{
  "success": true,
  "message": "知识条目添加成功",
  "doc_id": "a1b2c3d4e5f6",
  "data": {
    "category": "售后政策",
    "content_length": 15
  }
}
```

### 2.2 批量添加知识
**POST** `/api/v1/knowledge/add-batch`

批量添加多条知识。

**请求体**:
```json
[
  {
    "content": "工作时间：周一至周五 9:00-18:00",
    "category": "客服信息"
  },
  {
    "content": "支持微信、支付宝支付",
    "category": "支付方式"
  }
]
```

**响应示例**:
```json
{
  "success": true,
  "message": "成功添加 2 条知识",
  "data": {
    "doc_ids": ["doc1", "doc2"]
  }
}
```

### 2.3 检索知识
**GET** `/api/v1/knowledge/search`

根据查询文本检索相关知识。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | ✅ | - | 查询文本 |
| top_k | integer | ❌ | 3 | 返回结果数量 |
| category | string | ❌ | null | 过滤分类 |

**请求示例**:
```
GET /api/v1/knowledge/search?query=如何退货&top_k=3
```

**响应示例**:
```json
[
  {
    "content": "我们的产品支持7天无理由退货",
    "category": "售后政策",
    "score": 0.95,
    "metadata": {
      "source": "官网",
      "created_at": "2024-01-01T00:00:00"
    }
  },
  {
    "content": "退货流程：1. 申请退货...",
    "category": "售后政策",
    "score": 0.87,
    "metadata": {}
  }
]
```

### 2.4 删除知识
**DELETE** `/api/v1/knowledge/delete/{doc_id}`

根据文档ID删除知识条目。

**路径参数**:
- `doc_id`: 文档唯一标识

**响应示例**:
```json
{
  "success": true,
  "message": "知识条目删除成功",
  "doc_id": "a1b2c3d4e5f6"
}
```

### 2.5 获取知识库统计
**GET** `/api/v1/knowledge/count`

获取知识库的条目总数。

**响应示例**:
```json
{
  "total": 10,
  "message": "当前知识库共有 10 条记录"
}
```

### 2.6 清空知识库
**DELETE** `/api/v1/knowledge/clear`

⚠️ **危险操作**：清空所有知识库内容。

**查询参数**:
- `confirm`: boolean (必填，必须为true)

**请求示例**:
```
DELETE /api/v1/knowledge/clear?confirm=true
```

**响应示例**:
```json
{
  "success": true,
  "message": "知识库已清空"
}
```

---

## 3. RAG对话接口

### 3.1 RAG智能对话
**POST** `/api/v1/chat/`

基于知识库的智能对话，支持历史上下文。

**请求体**:
```json
{
  "question": "如何申请退货？",
  "image_url": null,
  "image_base64": null,
  "use_knowledge_base": true,
  "history": [
    {
      "role": "user",
      "content": "你好"
    },
    {
      "role": "assistant",
      "content": "您好，有什么可以帮您？"
    }
  ]
}
```

**参数说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | ✅ | 用户问题 (1-2000字符) |
| image_url | string | ❌ | 图片URL |
| image_base64 | string | ❌ | 图片Base64编码 |
| use_knowledge_base | boolean | ❌ | 是否使用知识库 (默认true) |
| history | array | ❌ | 历史对话 |

**响应示例**:
```json
{
  "answer": "您可以在收货后7天内申请退货。在订单页面点击申请退货，选择退货原因提交即可。",
  "confidence": "高",
  "knowledge_sources": [
    "我们的产品支持7天无理由退货",
    "退货流程：1. 在订单页面点击申请退货..."
  ],
  "model_used": "qwen-max",
  "has_image": false
}
```

### 3.2 图文对话
**POST** `/api/v1/chat/with-image`

支持上传图片的对话接口。

**Content-Type**: `multipart/form-data`

**表单字段**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | ✅ | 用户问题 |
| image | file | ❌ | 图片文件 |
| use_knowledge_base | boolean | ❌ | 是否使用知识库 |

**请求示例** (curl):
```bash
curl -X POST "http://localhost:8000/api/v1/chat/with-image" \
  -F "question=这是什么产品？" \
  -F "image=@/path/to/image.jpg" \
  -F "use_knowledge_base=true"
```

**响应格式**: 同3.1

### 3.3 简单对话
**GET** `/api/v1/chat/simple`

简化的对话接口，只需传入问题文本。

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| question | string | ✅ | - | 用户问题 |
| use_knowledge | boolean | ❌ | true | 是否使用知识库 |

**请求示例**:
```
GET /api/v1/chat/simple?question=你好&use_knowledge=false
```

**响应示例**:
```json
{
  "question": "你好",
  "answer": "您好！我是智能助手，有什么可以帮您的吗？"
}
```

### 3.4 对话服务健康检查
**GET** `/api/v1/chat/health`

检查对话服务状态。

**响应示例**:
```json
{
  "status": "healthy",
  "service": "RAG Chat Service",
  "message": "服务运行正常"
}
```

---

## 4. 错误码说明

| 状态码 | 说明 | 常见原因 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 201 | 创建成功 | 知识添加成功 |
| 400 | 请求参数错误 | 参数缺失或格式错误 |
| 404 | 资源不存在 | 文档ID不存在 |
| 500 | 服务器错误 | 模型调用失败、数据库错误 |

---

## 5. 使用示例

### Python示例

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000"

# 1. 添加知识
response = requests.post(
    f"{BASE_URL}/api/v1/knowledge/add",
    json={
        "content": "测试知识内容",
        "category": "测试",
    }
)
print(response.json())

# 2. RAG对话
response = requests.post(
    f"{BASE_URL}/api/v1/chat/",
    json={
        "question": "如何退货？",
        "use_knowledge_base": True,
    }
)
print(response.json())

# 3. 检索知识
response = requests.get(
    f"{BASE_URL}/api/v1/knowledge/search",
    params={"query": "退货", "top_k": 3}
)
print(response.json())
```

### JavaScript示例

```javascript
const BASE_URL = "http://localhost:8000";

// 1. 添加知识
fetch(`${BASE_URL}/api/v1/knowledge/add`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    content: "测试知识内容",
    category: "测试",
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));

// 2. RAG对话
fetch(`${BASE_URL}/api/v1/chat/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    question: "如何退货？",
    use_knowledge_base: true,
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

### curl示例

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 添加知识
curl -X POST "http://localhost:8000/api/v1/knowledge/add" \
  -H "Content-Type: application/json" \
  -d '{"content":"测试内容","category":"测试"}'

# 3. RAG对话
curl -X POST "http://localhost:8000/api/v1/chat/" \
  -H "Content-Type: application/json" \
  -d '{"question":"如何退货？","use_knowledge_base":true}'

# 4. 图文对话
curl -X POST "http://localhost:8000/api/v1/chat/with-image" \
  -F "question=这是什么？" \
  -F "image=@image.jpg"
```

---

## 6. 性能建议

1. **批量操作**: 使用批量接口减少请求次数
2. **缓存结果**: 缓存常见问答，减少API调用
3. **异步调用**: 使用异步方式提高并发
4. **限流**: 生产环境配置适当的限流策略
5. **超时设置**: 设置合理的请求超时时间 (建议60秒)

---

**文档版本**: 1.0  
**更新时间**: 2024-01-01

