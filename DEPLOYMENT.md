# Docker 部署成功！🎉

两个服务现在都已通过 Docker 成功部署并运行。

## 服务状态

✅ **message-sender** - healthy, 运行在 http://localhost:8000
✅ **daily-news** - running, 已连接到 message-sender
🌐 **daily-news Web 界面** - 运行在 http://localhost:8001

## 快速开始

### 方式 1: 统一部署（推荐）

从项目根目录部署两个服务：

```bash
cd /Users/heiwawa/work/demo/ai-tools

# 配置环境变量（首次）
cp message-sender/.env.example .env
vi .env  # 设置 WECOM_WEBHOOK_URL

# 启动所有服务
./start.sh

# 查看日志
./start.sh logs

# 测试 daily-news
./start.sh test

# 停止服务
./start.sh down
```

### 方式 2: 独立部署 message-sender

```bash
cd message-sender

# 配置环境变量
cp .env.example .env
vi .env

# Docker 模式
./start.sh docker

# 开发模式（带热重载）
./start.sh dev

# 查看日志
./start.sh logs

# 停止
./start.sh stop
```

## 可用命令

### 根目录 (ai-tools/start.sh)

```bash
./start.sh         # 启动所有服务
./start.sh down    # 停止所有服务
./start.sh restart # 重启服务
./start.sh build   # 重新构建镜像
./start.sh logs    # 查看所有日志
./start.sh logs daily-news  # 查看特定服务日志
./start.sh ps      # 查看容器状态
./start.sh test    # 测试 daily-news
./start.sh clean   # 完全清理
./start.sh help    # 帮助信息
```

### message-sender 目录

```bash
./start.sh         # 开发模式（默认）
./start.sh docker  # Docker 模式
./start.sh stop    # 停止容器
./start.sh logs    # 查看日志
./start.sh test    # 测试服务
./start.sh help    # 帮助信息
```

## 服务端点

### Message Sender
- **API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### Daily News
- **Web 界面**: http://localhost:8001
- **健康检查**: http://localhost:8001/api/health
- **手动推送**: http://localhost:8001/api/trigger
- **查看日志**: http://localhost:8001/api/logs

## Web 界面功能

Daily News 服务现在包含一个 Web 界面，可以通过浏览器访问 http://localhost:8001

功能包括：
- 📤 **手动推送新闻**: 点击按钮即可立即推送每日新闻
- 🔍 **查看服务状态**: 检查调度器、OCR 服务状态和下次运行时间
- 📊 **实时日志查看**: 自动刷新的日志显示，链接可点击
- 🎨 **彩色日志**: 错误、警告和信息消息使用不同颜色标记

详细文档请参考: [daily-news/WEB_INTERFACE.md](daily-news/WEB_INTERFACE.md)

## 测试消息发送

```bash
# 方式 1: 使用 start.sh
./start.sh test

# 方式 2: 直接 curl
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试消息",
    "content": "Hello from Docker!",
    "message_type": "text",
    "sender_type": "wecom"
  }'
```

## 已修复的问题

✅ **健康检查失败** - 在 Dockerfile 中添加了 curl
✅ **Node.js 安装问题** - 修复了 daily-news 的 Node.js 安装顺序
✅ **版本警告** - 移除了所有 docker-compose.yml 中的 `version` 字段
✅ **容器名称冲突** - 统一管理容器名称

## 文件结构

```
ai-tools/
├── start.sh              # 统一启动脚本
├── docker-compose.yml    # 统一编排配置
├── README.md             # 完整文档
├── message-sender/
│   ├── start.sh          # message-sender 启动脚本
│   ├── docker-compose.yml
│   ├── Dockerfile        # 包含 curl
│   └── DOCKER.md         # Docker 部署文档
└── daily-news/
    ├── start.sh          # daily-news 启动脚本
    ├── docker-compose.yml
    ├── Dockerfile        # 包含 Node.js + Tesseract.js
    └── OCR_README.md     # OCR 说明
```

## 下一步

1. ✅ 两个服务都已正常运行
2. ✅ 健康检查正常工作
3. ✅ daily-news 等待 message-sender 健康后才启动
4. ✅ OCR 功能集成（Node.js + Tesseract.js）

您现在可以：
- 查看日志：`./start.sh logs`
- 测试发送：`./start.sh test`
- 查看 API 文档：http://localhost:8000/docs

祝使用愉快！🚀
