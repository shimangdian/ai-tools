# Message Sender - Docker Deployment

快速部署指南，用于单独部署 Message Sender 服务。

## 快速开始

### 1. 配置环境变量

```bash
cd message-sender

# 复制环境变量模板
cp .env.example .env

# 编辑配置（设置你的 Webhook URL）
vi .env
```

### 2. Docker 部署

```bash
# 使用 Docker 启动
./start.sh docker
```

就这么简单！服务现在运行在 http://localhost:8000

## 可用命令

```bash
# 开发模式（默认，带热重载）
./start.sh
./start.sh dev

# Docker 模式
./start.sh docker      # 启动 Docker 容器
./start.sh stop        # 停止容器
./start.sh restart     # 重启容器
./start.sh build       # 重新构建镜像
./start.sh logs        # 查看日志
./start.sh ps          # 查看容器状态
./start.sh test        # 测试服务

# 帮助信息
./start.sh help
```

## 服务端点

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **发送消息**: POST http://localhost:8000/send

## 配置

### 环境变量（.env 文件）

```bash
# 企业微信配置
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY

# 钉钉配置（可选）
# DINGTALK_ENABLED=true
# DINGTALK_WEBHOOK_URL=your_webhook_url
# DINGTALK_SECRET=your_secret

# 飞书配置（可选）
# FEISHU_ENABLED=true
# FEISHU_WEBHOOK_URL=your_webhook_url
# FEISHU_SECRET=your_secret
```

## 测试

### 启动服务

```bash
./start.sh docker
```

### 测试健康检查

```bash
curl http://localhost:8000/health
```

### 发送测试消息

```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试消息",
    "content": "这是一条测试消息",
    "message_type": "text",
    "sender_type": "wecom"
  }'
```

## Docker 命令参考

### 查看日志

```bash
# 实时日志
./start.sh logs

# 或使用 docker compose
docker compose logs -f
```

### 重新构建

```bash
# 代码修改后重新构建
./start.sh build
./start.sh restart
```

### 进入容器

```bash
docker compose exec message-sender bash
```

### 清理

```bash
# 停止并删除容器
./start.sh stop

# 完全清理（包括镜像）
docker compose down --rmi all
```

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
./start.sh logs

# 检查容器状态
./start.sh ps
```

### 健康检查失败

```bash
# 测试健康端点
curl http://localhost:8000/health

# 查看应用日志
./start.sh logs
```

### 端口冲突

如果 8000 端口被占用，修改 `docker-compose.yml` 中的端口映射：

```yaml
ports:
  - "8001:8000"  # 改为其他端口
```

## 生产环境部署

1. 移除 `--reload` 标志（Dockerfile 已配置正确）
2. 设置环境变量而不是使用 .env 文件
3. 使用反向代理（Nginx/Traefik）
4. 配置 HTTPS
5. 设置监控和日志收集

## 与 Daily News 集成

如果需要与 daily-news 服务集成，请使用父目录的统一部署：

```bash
cd ..
./start.sh
```

这将同时启动 message-sender 和 daily-news 服务。
