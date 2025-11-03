# 前端 Dockerfile - 抗衰老专家咨询系统
# 阶段1：构建
FROM node:18-slim AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖（Vite 构建需要所有依赖）
RUN npm install

# 复制源代码
COPY . .

# 设置 API URL（生产环境）
ENV VITE_API_URL=http://106.14.204.36/api

# 构建生产版本
RUN npm run build

# 阶段2：运行
FROM nginx:alpine

# 复制构建产物（Vite 输出目录是 build）
COPY --from=builder /app/build /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]

