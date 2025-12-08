# AI Tools - Docker Deployment

This directory contains two services that work together:
- **message-sender**: A message sending service that supports WeCom, DingTalk, and Feishu
- **daily-news**: A daily news fetcher and sender with OCR support

## Prerequisites

- Docker (https://docs.docker.com/get-docker/)
- Docker Compose (https://docs.docker.com/compose/install/)

## Quick Start

1. **Configure Environment Variables**

```bash
# Copy the example .env file
cp message-sender/.env.example .env

# Edit .env with your configuration
vi .env
```

2. **Start Services**

```bash
./start.sh
```

Or use Docker Compose directly:

```bash
docker compose up -d
```

3. **View Logs**

```bash
./start.sh logs
```

4. **Test Daily News**

```bash
./start.sh test
```

## Available Commands

```bash
./start.sh            # Start all services
./start.sh down       # Stop all services
./start.sh restart    # Restart all services
./start.sh build      # Rebuild Docker images
./start.sh logs       # View all logs
./start.sh logs daily-news  # View specific service logs
./start.sh ps         # Show running containers
./start.sh test       # Run daily news task once
./start.sh clean      # Remove all containers and images
./start.sh help       # Show help message
```

## Services

### Message Sender Service

- **Port**: 8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Daily News Service

- Automatically fetches and sends news at 08:00 (configurable)
- Uses Tesseract.js for OCR text extraction
- Sends formatted news via Message Sender Service

## Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# WeCom Configuration
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY

# Schedule Configuration (in docker-compose.yml)
SCHEDULE_HOUR=8
SCHEDULE_MINUTE=0
SCHEDULE_TIMEZONE=Asia/Shanghai
```

### Config Files

- `message-sender/config.yaml`: Message sender configuration
- `daily-news/config.yaml`: Daily news configuration

## Development

### Rebuild After Code Changes

```bash
./start.sh build
./start.sh restart
```

### Execute Commands in Container

```bash
# Enter daily-news container
./start.sh exec daily-news bash

# Enter message-sender container
./start.sh exec message-sender bash
```

### View Real-time Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f daily-news
```

## Troubleshooting

### Services won't start

```bash
# Check service status
./start.sh ps

# View detailed logs
./start.sh logs
```

### Reset Everything

```bash
# Stop and remove all containers, volumes, and images
./start.sh clean

# Start fresh
./start.sh build
./start.sh up
```

### Test OCR Functionality

```bash
# Run a single test
docker compose exec daily-news python -m app.main --run-once
```

## Production Deployment

1. Remove development volume mounts from `docker-compose.yml`
2. Set proper restart policies
3. Configure logging drivers
4. Use Docker secrets for sensitive data
5. Set up monitoring and alerts

## Architecture

```
┌─────────────────┐
│  Daily News     │
│  - Fetch News   │
│  - OCR (Node.js)│
│  - Schedule     │
└────────┬────────┘
         │
         │ HTTP
         ▼
┌─────────────────┐
│ Message Sender  │
│  - WeCom        │
│  - DingTalk     │
│  - Feishu       │
└─────────────────┘
```

## License

MIT
