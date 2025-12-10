# Daily News Web Interface

Web interface for managing and monitoring the Daily News service.

## Features

- **Manual Message Sending**: Trigger news fetching and sending on-demand
- **Service Health Check**: Monitor service status, scheduler, and OCR configuration
- **Live Log Viewing**: View service logs with automatic refresh
- **Link Highlighting**: URLs in logs are automatically converted to clickable links
- **Color-Coded Logs**: Errors, warnings, and info messages are color-coded for easy reading

## Accessing the Web Interface

After starting the service with Docker:

```bash
# Start the service
docker compose up -d

# Access the web interface
open http://localhost:8001
```

## Web Interface Features

### 1. Manual Push Section

- **立即推送新闻** (Push News Now): Manually trigger the daily news fetching and sending process
- **检查服务状态** (Check Service Status): View the current service health including:
  - Scheduler running status
  - OCR service enabled status
  - Next scheduled run time

### 2. Service Logs Section

- **刷新日志** (Refresh Logs): Reload the latest logs
- **清空显示** (Clear Display): Clear the log display (doesn't delete actual logs)
- **Auto-refresh**: Logs automatically refresh every 30 seconds
- **Statistics Display**:
  - Log line count
  - Last update timestamp

### 3. Log Features

- **URL Highlighting**: All URLs in logs are automatically converted to clickable links
- **Color Coding**:
  - Red: Error messages
  - Yellow: Warning messages
  - Blue: Info messages
  - White: General log entries
- **Line Limit**: Shows the last 100 lines by default (configurable)

## API Endpoints

The web interface uses the following API endpoints:

### GET /
Main web interface HTML page

### POST /api/trigger
Manually trigger news sending

**Response:**
```json
{
  "success": true,
  "message": "新闻推送任务已成功执行"
}
```

### GET /api/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "details": {
    "scheduler_running": true,
    "ocr_enabled": true,
    "next_run_time": "2025-12-11 08:00:00"
  }
}
```

### GET /api/logs?lines=100
Get service logs

**Parameters:**
- `lines` (optional): Number of log lines to retrieve (default: 100)

**Response:**
```json
{
  "logs": "2025-12-10 01:36:00 - INFO - Service started...",
  "total_lines": 50
}
```

## Usage Examples

### Manual Trigger via Command Line

```bash
# Trigger news sending
curl -X POST http://localhost:8001/api/trigger

# Check health
curl http://localhost:8001/api/health

# Get last 50 log lines
curl "http://localhost:8001/api/logs?lines=50"
```

### Integration with Other Tools

You can integrate the API endpoints with:
- CI/CD pipelines for automated testing
- Monitoring tools (Prometheus, Grafana)
- Custom dashboards
- Mobile apps

## Technical Details

### Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Pure HTML/CSS/JavaScript (no external dependencies)
- **Styling**: Modern gradient design with responsive layout
- **Auto-refresh**: JavaScript setInterval for periodic updates

### Port Configuration

- Default port: **8001**
- Configurable in `docker-compose.yml`:
  ```yaml
  ports:
    - "8001:8001"  # Change the first 8001 to use a different host port
  ```

### Logging

The web interface displays logs from:
1. File logs: `/app/logs/daily_news.log` (if available)
2. Container stdout logs (via Docker logs)

### Security Considerations

- The web interface is currently without authentication
- Recommended for internal/development use only
- For production, consider adding:
  - API key authentication
  - Rate limiting
  - HTTPS/SSL
  - Firewall rules to restrict access

## Troubleshooting

### Web Interface Not Accessible

```bash
# Check if container is running
docker compose ps

# Check logs for errors
docker compose logs daily-news

# Verify port mapping
docker compose port daily-news 8001
```

### Manual Trigger Not Working

1. Check message-sender service is running:
   ```bash
   docker compose ps message-sender
   ```

2. Verify webhook URL is configured:
   ```bash
   docker compose logs daily-news | grep webhook
   ```

3. Check error messages in logs:
   ```bash
   docker compose logs daily-news --tail 50
   ```

### Logs Not Showing

The log viewer shows container stdout/stderr logs. If no logs appear:
1. Trigger a manual send to generate logs
2. Check if logs directory is mounted correctly in `docker-compose.yml`
3. Verify logging configuration in `app/main.py`

## Development

### Running Locally Without Docker

```bash
cd daily-news

# Install dependencies
pip install -r requirements.txt

# Start the web API
uvicorn app.web_api:app --host 0.0.0.0 --port 8001 --reload
```

### Customizing the Interface

The web interface HTML is embedded in [app/web_api.py](app/web_api.py#L111). To customize:

1. Locate the `@app.get("/")` endpoint
2. Modify the HTML in the `html_content` string
3. Rebuild the container: `docker compose up -d --build`

### Adding New Endpoints

Add new FastAPI endpoints in [app/web_api.py](app/web_api.py):

```python
@app.get("/api/your-endpoint")
async def your_endpoint():
    return {"status": "ok"}
```

## Screenshots

The interface features:
- Clean, modern design with gradient backgrounds
- Responsive layout for mobile and desktop
- Interactive buttons with hover effects
- Auto-refreshing log viewer with syntax highlighting

## Future Enhancements

Potential improvements:
- [ ] User authentication and authorization
- [ ] Historical statistics and charts
- [ ] Email/SMS notification configuration
- [ ] Multiple webhook management
- [ ] Scheduled task management UI
- [ ] Log search and filtering
- [ ] Export logs functionality
- [ ] Dark/light theme toggle
