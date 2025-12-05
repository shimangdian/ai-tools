# Daily News Service

每日新闻自动推送服务，每天早上 8 点自动获取每日早报并推送到企业微信。

## 功能特性

- ⏰ 定时任务：每天早上 8 点自动执行
- 📰 新闻获取：从 API 获取每日早报图片
- 🔍 OCR 识别：使用 MinerU/PaddleOCR 提取图片中的文字内容
- 📤 消息推送：自动推送到企业微信（优先发送 OCR 文字版，失败时发送图片）
- 🔄 异步处理：高性能异步任务执行
- ⚙️ 灵活配置：支持 YAML 文件和环境变量
- 🐳 Docker 部署：开箱即用的容器化部署
- 📝 多种格式：支持文本消息和 Markdown 图片消息

## 系统架构

```
daily-news (每日新闻服务)
    ↓
    ├─ 定时任务调度 (每天 8:00)
    ↓
    ├─ 获取新闻 API (https://dwz.2xb.cn/zaob)
    ↓
    ├─ 解析 imageUrl
    ↓
    ├─ 生成 Markdown 消息
    ↓
    └─ 调用 message-sender 服务推送到企业微信
```

## 快速开始

### 前置条件

1. **message-sender 服务已启动** (见 ../message-sender/README.md)
2. 已配置企业微信 Webhook

### 方式一：Docker Compose（推荐）

1. 配置环境变量：
```bash
cd daily-news
cp .env.example .env
```

2. 编辑 `.env` 文件，填入企业微信 Webhook：
```bash
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

3. 构建并启动服务：
```bash
# 先构建 message-sender 镜像
cd ../message-sender
docker build -t message-sender:latest .

# 启动 daily-news 服务（包含 message-sender）
cd ../daily-news
docker-compose up -d
```

4. 查看日志：
```bash
docker-compose logs -f daily-news
```

### 方式二：本地运行

1. 确保 message-sender 服务已启动：
```bash
cd ../message-sender
./start.sh
```

2. 安装依赖：
```bash
cd ../daily-news
pip install -r requirements.txt
```

3. 配置环境变量或修改 `config.yaml`

4. 启动服务：
```bash
./start.sh
```

### 测试立即执行

不等待定时任务，立即执行一次：

```bash
# Docker 方式
docker exec daily-news python -m app.main --run-once

# 本地方式
python -m app.main --run-once
```

## 配置说明

### 配置文件 (config.yaml)

```yaml
# 新闻 API 配置
news:
  api_url: "https://dwz.2xb.cn/zaob"

# 消息推送服务配置
message_sender:
  base_url: "http://localhost:8000"
  api_key: ""  # 可选

# 定时任务配置
schedule:
  enabled: true
  hour: 8      # 执行时间：8点
  minute: 0    # 执行分钟：0分
  timezone: "Asia/Shanghai"

# OCR 配置
ocr:
  enabled: true  # 是否启用 OCR 文字识别
```

### OCR 引擎说明

系统支持两种 OCR 引擎：

1. **MinerU (推荐)**: 专为文档解析设计，对长图和复杂排版支持更好
   - 安装：`pip install magic-pdf[full]`
   - 适用场景：新闻早报、文档图片等长图

2. **PaddleOCR (备选)**: 通用 OCR 引擎，作为 MinerU 不可用时的备选方案
   - 自动在 MinerU 不可用时启用
   - 适用场景：通用图片文字识别

系统会优先尝试使用 MinerU，如果未安装或识别失败，会自动降级到 PaddleOCR 或直接发送图片。

### 消息发送策略

1. **OCR 启用时**：
   - 首先尝试使用 OCR 提取文字内容
   - 如果提取成功（文字长度 > 10），发送纯文本消息
   - 如果提取失败或内容过短，降级为发送图片（markdown_v2 格式）

2. **OCR 禁用时**：
   - 直接发送图片（markdown_v2 格式）

```

### 环境变量

```bash
# 新闻 API 配置
NEWS_API_URL=https://dwz.2xb.cn/zaob

# 消息推送服务配置
MESSAGE_SENDER_URL=http://localhost:8000
MESSAGE_SENDER_API_KEY=your_api_key  # 可选

# 定时任务配置
SCHEDULE_ENABLED=true
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
SCHEDULE_TIMEZONE=Asia/Shanghai

# OCR 配置
OCR_ENABLED=true  # 是否启用 OCR 文字识别
```

## 使用示例

### 1. 作为服务运行

服务启动后会在后台运行，每天早上 8 点自动执行：

```bash
./start.sh
```

日志输出：
```
2025-01-01 08:00:00 - INFO - Starting daily news task...
2025-01-01 08:00:01 - INFO - Fetched news image URL: https://example.com/news.jpg
2025-01-01 08:00:02 - INFO - Daily news sent successfully
```

### 2. 手动执行一次

```bash
python -m app.main --run-once
```

### 3. 自定义配置文件

```bash
python -m app.main --config /path/to/config.yaml
```

## 消息格式

推送到企业微信的消息有两种格式：

### 1. OCR 文字版（优先）

当 OCR 成功提取文字时，发送纯文本消息：

```
📰 每日早报 - 2025-01-01

[从图片中识别出的新闻文字内容]

---
每日 8 点自动推送 | 图片转文字版
```

### 2. 图片版（降级）

当 OCR 失败或禁用时，发送 markdown_v2 格式消息：

```markdown
## 📰 每日早报

**日期**: 2025-01-01

![早报](https://example.com/news.jpg)

---
*每日 8 点自动推送*
```

## 项目结构

```
daily-news/
├── app/
│   ├── __init__.py
│   ├── main.py              # 主程序入口
│   ├── config.py            # 配置管理
│   ├── news_fetcher.py      # 新闻获取模块
│   ├── message_sender.py    # 消息推送客户端
│   ├── ocr_service.py       # OCR 服务 (MinerU/PaddleOCR)
│   └── scheduler.py         # 定时任务调度器
├── logs/                    # 日志目录
├── config.yaml              # 配置文件
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像
├── docker-compose.yml       # Docker Compose 配置
├── start.sh                 # 启动脚本
└── README.md                # 项目文档
```

## API 响应格式

新闻 API (https://dwz.2xb.cn/zaob) 预期返回格式：

```json
{
  "imageUrl": "https://example.com/news.jpg"
}
```

或其他可能的字段名：
- `image_url`
- `imageURL`
- `img_url`
- `imgUrl`
- `url`
- `image`

程序会自动尝试这些字段名。

## 常见问题

### 1. 消息发送失败

检查：
- message-sender 服务是否正常运行
- 企业微信 Webhook URL 是否正确
- 网络连接是否正常

```bash
# 测试 message-sender 服务
curl http://localhost:8000/health
```

### 2. 新闻图片获取失败

检查：
- 新闻 API 是否可访问
- API 返回的数据格式是否正确

```bash
# 测试新闻 API
curl https://dwz.2xb.cn/zaob
```

### 3. 定时任务没有执行

检查：
- `SCHEDULE_ENABLED` 是否设置为 `true`
- 时区配置是否正确
- 查看日志确认调度器状态

```bash
# 查看日志
tail -f logs/daily_news.log
# 或
docker-compose logs -f daily-news
```

### 4. 修改执行时间

编辑配置文件或环境变量：

```yaml
schedule:
  hour: 9      # 改为 9 点执行
  minute: 30   # 改为 30 分执行
```

或设置环境变量：
```bash
SCHEDULE_HOUR=9
SCHEDULE_MINUTE=30
```

重启服务生效。

### 5. OCR 识别失败或提取不到文字

检查：
- MinerU 是否正确安装：`pip install magic-pdf[full]`
- 查看日志确认使用的 OCR 引擎（MinerU 或 PaddleOCR）
- 图片格式和质量是否符合要求
- 如果 MinerU 失败，系统会自动降级到 PaddleOCR

```bash
# 测试 OCR 功能
python -m app.main --run-once
# 查看日志
tail -f logs/daily_news.log
```

如果 OCR 持续失败，可以禁用 OCR，直接发送图片：
```yaml
ocr:
  enabled: false
```

### 6. 安装 MinerU 失败

MinerU 依赖较多，如果安装失败：
1. 确保使用 Python 3.8+
2. 尝试使用虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install magic-pdf[full]
```
3. 如果仍然失败，系统会自动使用 PaddleOCR 作为备选

## 日志管理

日志文件位置：
- Docker: `./logs/daily_news.log`
- 本地: `./daily_news.log`

日志级别可以通过修改 `app/main.py` 中的 `logging.basicConfig` 调整。

## 扩展功能

### 支持其他推送渠道

修改 `app/message_sender.py`，调用不同的 sender_type：

```python
# 推送到钉钉
result = await self.send_message(
    title=title,
    content=content,
    message_type="markdown",
    sender_type="dingtalk"  # 改为 dingtalk 或 feishu
)
```

### 支持其他新闻源

修改 `config.yaml` 中的 `news.api_url`：

```yaml
news:
  api_url: "https://your-news-api.com/endpoint"
```

### 自定义消息格式

修改 `app/message_sender.py` 中的 `create_wecom_markdown_message` 方法。

## 监控和告警

建议配置以下监控：

1. **健康检查**：定期检查服务是否运行
2. **日志监控**：监控错误日志
3. **推送成功率**：统计推送成功/失败次数

可以配置额外的告警通知，当任务失败时发送告警消息。

## 安全建议

1. 不要将 Webhook URL 提交到版本控制系统
2. 使用环境变量或密钥管理工具存储敏感信息
3. 限制服务访问权限
4. 定期更新依赖包

## 依赖服务

- **message-sender**: 消息推送服务 (见 ../message-sender/)
- **新闻 API**: https://dwz.2xb.cn/zaob

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
