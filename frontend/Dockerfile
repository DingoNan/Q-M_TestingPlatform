# ===== 阶段 1：构建前端静态资源 =====
FROM node:20-alpine AS builder

WORKDIR /app

# 加大 Node 堆内存上限，避免 vue-cli/webpack 构建时 OOM(默认 1GB 不够)
ENV NODE_OPTIONS=--max-old-space-size=8192

# 先拷贝依赖清单，利用 docker 层缓存
COPY package.json ./
RUN npm config set registry https://registry.npmmirror.com && \
    npm install --legacy-peer-deps

# 拷贝源码并构建
COPY . .
RUN npm run build

# ===== 阶段 2：nginx 托管静态资源 =====
FROM nginx:alpine

# 清空默认站点目录，拷贝构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 自定义 nginx 配置（hash 路由 SPA）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
