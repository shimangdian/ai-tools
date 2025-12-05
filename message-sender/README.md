# Message Sender Service

一个统一的消息推送服务，支持企业微信、钉钉、飞书等多种推送渠道。

## 功能特性

- 🚀 支持多种推送渠道
  - 企业微信（WeCom）
  - 钉钉（DingTalk）
  - 飞书（Feishu/Lark）
- 🔌 RESTful API 接口
- 🔐 支持 API Key 认证
- 🐳 Docker 容器化部署
- ⚙️ 灵活的配置方式（YAML 文件 + 环境变量）
- 📝 支持多种消息类型（文本、Markdown 等）
- 🎯 支持 @特定用户或全员
- 📊 自动日志记录
- 💪 异步处理，高性能

## 快速开始

### 方式一：使用 Docker（推荐）

1. 克隆或复制 `message-sender` 文件夹

2. 配置环境变量，复制 `.env.example` 为 `.env` 并填入配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，至少配置一个推送渠道：
```bash
# 企业微信配置
WECOM_ENABLED=true
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY_HERE
```

3. 启动服务：
```bash
docker-compose up -d
```

4. 查看日志：
```bash
docker-compose logs -f
```

### 方式二：本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量或修改 `config.yaml`

3. 启动服务：
```bash
./start.sh
# 或者
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 配置说明

### 企业微信（WeCom）

1. 在企业微信管理后台创建群机器人
2. 获取 Webhook URL（格式：`https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx`）
3. 配置：

```yaml
# config.yaml
senders:
  wecom:
    enabled: true
    webhook_url: "你的webhook_url"
    mentioned_list: []  # 可选：@特定用户，如 ["@all"]
    mentioned_mobile_list: []  # 可选：@特定手机号
```

或使用环境变量：
```bash
WECOM_ENABLED=true
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

### 钉钉（DingTalk）

1. 在钉钉群创建自定义机器人
2. 获取 Webhook URL 和加签密钥（可选）
3. 配置：

```yaml
# config.yaml
senders:
  dingtalk:
    enabled: true
    webhook_url: "你的webhook_url"
    secret: "加签密钥（可选）"
    at_mobiles: []  # 可选：@特定手机号
    at_all: false  # 可选：@所有人
```

或使用环境变量：
```bash
DINGTALK_ENABLED=true
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN
DINGTALK_SECRET=your_secret  # 可选
```

### 飞书（Feishu）

1. 在飞书群创建自定义机器人
2. 获取 Webhook URL
3. 配置：

```yaml
# config.yaml
senders:
  feishu:
    enabled: true
    webhook_url: "你的webhook_url"
    secret: "加签密钥（可选）"
```

或使用环境变量：
```bash
FEISHU_ENABLED=true
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_HOOK_ID
FEISHU_SECRET=your_secret  # 可选
```

### API 认证（可选）

配置 API Key 以保护接口：

```yaml
# config.yaml
api:
  api_key: "your_secret_api_key"
```

或使用环境变量：
```bash
API_KEY=your_secret_api_key
```

## API 使用

### 接口文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 发送消息

**发送到所有配置的渠道：**

```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "title": "系统告警",
    "content": "服务器 CPU 使用率超过 80%",
    "message_type": "text"
  }'
```

**发送到指定渠道（企业微信）：**

```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "title": "系统告警",
    "content": "服务器 CPU 使用率超过 80%",
    "message_type": "text",
    "sender_type": "wecom",
    "extra": {
      "mentioned_list": ["@all"]
    }
  }'
```

**发送 Markdown 消息：**

```bash
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "title": "系统告警",
    "content": "## CPU 告警\n\n- **服务器**: server-01\n- **使用率**: 85%\n- **时间**: 2025-01-01 12:00:00",
    "message_type": "markdown",
    "sender_type": "wecom"
  }'
```

### 查询可用渠道

```bash
curl http://localhost:8000/senders \
  -H "X-API-Key: your_api_key"
```

### 健康检查

```bash
curl http://localhost:8000/health
```

## Python 调用示例

```python
import requests

def send_message(title, content, sender_type=None):
    url = "http://localhost:8000/send"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "your_api_key"  # 如果配置了 API Key
    }
    data = {
        "title": title,
        "content": content,
        "message_type": "text",
        "sender_type": sender_type  # None=所有渠道，"wecom"=企业微信
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

# 发送到所有渠道
result = send_message("测试标题", "测试内容")
print(result)

# 只发送到企业微信
result = send_message("测试标题", "测试内容", sender_type="wecom")
print(result)
```

## 项目结构

```
message-sender/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用
│   ├── config.py            # 配置管理
│   ├── models.py            # 数据模型
│   └── senders/
│       ├── __init__.py
│       ├── base.py          # 基础发送器接口
│       ├── wecom.py         # 企业微信发送器
│       ├── dingtalk.py      # 钉钉发送器
│       ├── feishu.py        # 飞书发送器
│       └── manager.py       # 发送器管理器
├── tests/                   # 测试目录（待完善）
├── config.yaml              # 配置文件
├── .env.example             # 环境变量示例
├── requirements.txt         # Python 依赖
├── Dockerfile               # Docker 镜像
├── docker-compose.yml       # Docker Compose 配置
├── start.sh                 # 启动脚本
└── README.md                # 项目文档
```

## 扩展新渠道

要添加新的推送渠道，按以下步骤操作：

1. 在 `app/senders/` 目录创建新的发送器类，继承 `BaseSender`
2. 实现 `send()` 和 `validate_config()` 方法
3. 在 `app/senders/manager.py` 的 `SENDER_CLASSES` 字典中注册
4. 在 `config.yaml` 和 `.env.example` 中添加配置说明

示例：

```python
# app/senders/telegram.py
from .base import BaseSender

class TelegramSender(BaseSender):
    def __init__(self, config):
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.chat_id = config.get("chat_id")

    def validate_config(self):
        return bool(self.bot_token and self.chat_id)

    async def send(self, title, content, message_type="text", extra=None):
        # 实现发送逻辑
        pass
```

## 常见问题

### 1. Docker 容器无法连接网络

检查 Docker 网络配置，确保容器可以访问外网。

### 2. 企业微信消息发送失败

- 检查 Webhook URL 是否正确
- 确认机器人没有被禁用
- 检查消息内容是否符合企业微信规范

### 3. 如何同时推送到多个渠道

不指定 `sender_type` 参数即可推送到所有启用的渠道：

```json
{
  "title": "标题",
  "content": "内容"
}
```

## 安全建议

1. 生产环境务必配置 API Key
2. 不要将 Webhook URL 和密钥提交到版本控制系统
3. 使用 HTTPS 部署服务
4. 定期更新依赖包
5. 限制服务访问来源（防火墙/网络策略）

## License

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
