# 安全配置指南

## ⚠️ 重要提示

本项目包含敏感配置信息，请务必遵循以下安全规范：

## 🔐 敏感文件说明

以下文件包含敏感信息，**已被 `.gitignore` 忽略，不会提交到 Git**：

### 后端配置文件
- `backend/env_template.txt` - 后端环境变量配置（包含 API Key）
- `env.production.template` - 生产环境配置（包含 API Key）
- `.env` - 本地环境变量文件

### 对应的示例文件（可以提交）
- `backend/env_template.txt.example` - 后端配置模板
- `env.production.template.example` - 生产环境配置模板
- `.env.example` - 环境变量示例

## 📝 首次配置步骤

### 1. 复制配置模板

```bash
# 后端配置
cp backend/env_template.txt.example backend/env_template.txt

# 生产环境配置（如需部署）
cp env.production.template.example env.production.template
```

### 2. 填入真实配置

编辑复制的文件，填入真实的配置值：

```bash
# 编辑后端配置
nano backend/env_template.txt

# 编辑生产环境配置
nano env.production.template
```

**必须修改的配置项：**
- `DASHSCOPE_API_KEY` - 阿里云 DashScope API 密钥

### 3. 获取 API 密钥

#### 阿里云 DashScope API Key
1. 访问：https://dashscope.console.aliyun.com/apiKey
2. 登录阿里云账号
3. 创建或获取 API Key
4. 复制并粘贴到配置文件中

## 🔒 安全最佳实践

### 1. 永远不要提交敏感信息

❌ **禁止操作：**
```bash
# 不要将包含真实密钥的文件添加到 Git
git add backend/env_template.txt
git add env.production.template
```

✅ **正确操作：**
```bash
# 只提交示例文件
git add backend/env_template.txt.example
git add env.production.template.example
```

### 2. 检查是否泄露

提交前务必检查：

```bash
# 查看将要提交的文件
git status

# 查看文件差异
git diff --cached

# 确保没有包含 API Key
grep -r "sk-" .git/index 2>/dev/null || echo "安全：未发现 API Key"
```

### 3. 使用环境变量

生产环境建议使用环境变量而不是配置文件：

```bash
# 设置环境变量
export DASHSCOPE_API_KEY=your-api-key-here

# 启动应用
python run.py
```

## 🚨 如果不小心提交了敏感信息

### 立即处理步骤：

1. **从当前提交中移除**

```bash
# 从 Git 缓存中移除
git rm --cached backend/env_template.txt
git rm --cached env.production.template

# 提交删除操作
git commit -m "移除敏感配置文件"
```

2. **更换泄露的密钥**

- 立即前往阿里云控制台
- 删除或禁用泄露的 API Key
- 生成新的 API Key
- 更新本地配置文件

3. **清理 Git 历史（可选但推荐）**

```bash
# 使用 git-filter-repo 清理历史
# 安装: pip install git-filter-repo

# 从所有历史中移除敏感文件
git filter-repo --path backend/env_template.txt --invert-paths
git filter-repo --path env.production.template --invert-paths

# 强制推送（警告：会改写历史）
git push origin --force --all
```

## 📋 配置文件清单

### 已被 `.gitignore` 忽略的文件：

```
backend/env_template.txt          # ❌ 不提交（包含真实密钥）
env.production.template           # ❌ 不提交（包含真实密钥）
.env                              # ❌ 不提交
.env.local                        # ❌ 不提交
.env.production                   # ❌ 不提交
volumes/                          # ❌ 不提交（Docker 数据）
*.log                             # ❌ 不提交（日志文件）
```

### 可以提交的文件：

```
backend/env_template.txt.example  # ✅ 可提交（示例模板）
env.production.template.example   # ✅ 可提交（示例模板）
.env.example                      # ✅ 可提交（示例模板）
.gitignore                        # ✅ 可提交
SECURITY.md                       # ✅ 可提交
```

## 🔍 定期安全检查

### 每次提交前检查：

```bash
# 1. 查看即将提交的文件
git status

# 2. 搜索可能的敏感信息
git diff --cached | grep -i "api.*key\|password\|secret\|token"

# 3. 确认 .gitignore 生效
git check-ignore backend/env_template.txt
# 应该输出：backend/env_template.txt
```

### 定期审计：

```bash
# 检查已提交的文件中是否有敏感信息
git log -p | grep -i "sk-\|api.*key\|secret"
```

## 📞 报告安全问题

如果发现本项目的安全问题，请：
1. **不要**公开提交 issue
2. 直接联系项目维护者
3. 提供详细的问题描述

## 🎯 团队协作建议

### 新成员加入时：

1. 提供此文档
2. 确保理解安全规范
3. 协助配置本地环境
4. 提供测试用的 API Key（非生产环境）

### Code Review 检查点：

- [ ] 没有提交包含真实密钥的文件
- [ ] `.gitignore` 规则正确
- [ ] 配置文件使用示例值
- [ ] 文档中没有敏感信息

## 📚 相关资源

- [阿里云 DashScope 文档](https://help.aliyun.com/zh/dashscope/)
- [Git Security Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Credentials-Storage)
- [环境变量管理](https://12factor.net/config)

---

**记住：安全无小事，配置需谨慎！** 🔐

