"""Web API for Daily News Service"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import load_config
from .news_fetcher import NewsFetcher
from .message_sender import MessageSender
from .scheduler import DailyNewsScheduler

# Setup logging to file
log_dir = Path("/app/logs")
if not log_dir.exists():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

log_file = log_dir / "daily_news.log"

# Get root logger and configure it
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Remove existing handlers to avoid duplicates
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Add stdout handler
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdout_handler.setFormatter(stdout_formatter)
root_logger.addHandler(stdout_handler)

# Add file handler with immediate flush
file_handler = logging.FileHandler(log_file, mode='a')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(stdout_formatter)
root_logger.addHandler(file_handler)

# Force flush after every log
class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

# Replace file handler with flush handler
root_logger.removeHandler(file_handler)
flush_handler = FlushFileHandler(log_file, mode='a')
flush_handler.setLevel(logging.INFO)
flush_handler.setFormatter(stdout_formatter)
root_logger.addHandler(flush_handler)

logger = logging.getLogger(__name__)
logger.info(f"Web API starting, logging to {log_file}")

# Create FastAPI app
app = FastAPI(title="Daily News Service", version="1.0.0")

# Global service instance
service_scheduler: Optional[DailyNewsScheduler] = None


class TriggerResponse(BaseModel):
    """Response for manual trigger"""
    success: bool
    message: str
    details: Optional[dict] = None


class LogResponse(BaseModel):
    """Response for log viewing"""
    logs: str
    total_lines: int


def get_scheduler() -> DailyNewsScheduler:
    """Get or create scheduler instance"""
    global service_scheduler

    if service_scheduler is None:
        # Load config
        config = load_config()

        # Initialize news fetcher
        news_api_url = config["news"]["api_url"]
        news_fetcher = NewsFetcher(news_api_url)

        # Initialize message sender
        sender_config = config["message_sender"]
        message_sender = MessageSender(
            base_url=sender_config["base_url"],
            api_key=sender_config.get("api_key")
        )

        # Initialize scheduler
        schedule_config = config["schedule"]
        ocr_config = config.get("ocr", {})
        service_scheduler = DailyNewsScheduler(
            news_fetcher=news_fetcher,
            message_sender=message_sender,
            timezone=schedule_config["timezone"],
            use_ocr=ocr_config.get("enabled", True),
            max_image_side=ocr_config.get("max_image_side", 8000),
            ocr_api_url=ocr_config.get("api_url"),
            ocr_token=ocr_config.get("token")
        )

        # Schedule daily task if enabled
        if schedule_config["enabled"]:
            service_scheduler.schedule_daily_task(
                hour=schedule_config["hour"],
                minute=schedule_config["minute"]
            )
            service_scheduler.start()
            logger.info(
                f"Scheduler started at {schedule_config['hour']:02d}:{schedule_config['minute']:02d} "
                f"{schedule_config['timezone']}"
            )

    return service_scheduler


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Starting Daily News Web API...")
    get_scheduler()
    logger.info("Daily News Web API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global service_scheduler
    if service_scheduler:
        service_scheduler.shutdown()
    logger.info("Daily News Web API shut down")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the web interface"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily News Service</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }

        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .header p {
            color: #666;
            font-size: 1.1em;
        }

        .card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        .card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: white;
        }

        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.4);
        }

        .btn-success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .btn-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }

        .status-box {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }

        .status-info {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #1976d2;
        }

        .status-success {
            background: #e8f5e9;
            color: #388e3c;
            border-left: 4px solid #388e3c;
        }

        .status-error {
            background: #ffebee;
            color: #d32f2f;
            border-left: 4px solid #d32f2f;
        }

        .log-container {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
            max-height: 600px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .log-container a {
            color: #4fc3f7;
            text-decoration: none;
        }

        .log-container a:hover {
            text-decoration: underline;
        }

        .log-line {
            margin-bottom: 4px;
        }

        .log-error {
            color: #f48771;
        }

        .log-warning {
            color: #dcdcaa;
        }

        .log-info {
            color: #4fc3f7;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-item {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
    </style>
    <script>
        // Define all functions before DOM loads
        function showStatus(message, type) {
            const statusBox = document.getElementById('statusBox');
            statusBox.className = 'status-box status-' + type;
            statusBox.innerHTML = message;
            statusBox.style.display = 'block';

            if (type === 'success' || type === 'error') {
                setTimeout(() => {
                    statusBox.style.display = 'none';
                }, 5000);
            }
        }

        async function triggerNews() {
            const btn = document.getElementById('triggerBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> 推送中...';

            showStatus('正在获取并推送每日新闻...', 'info');

            try {
                const response = await fetch('/api/trigger', {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.success) {
                    showStatus('✅ ' + data.message, 'success');
                    // Auto refresh logs after successful trigger
                    setTimeout(() => loadLogs(), 2000);
                } else {
                    showStatus('❌ ' + data.message, 'error');
                }
            } catch (error) {
                showStatus('❌ 请求失败: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '立即推送新闻';
            }
        }

        async function checkHealth() {
            const btn = document.getElementById('healthBtn');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span> 检查中...';

            try {
                const response = await fetch('/api/health');
                const data = await response.json();

                const details = data.details || {};
                const statusMsg = `
                    ✅ 服务运行正常<br>
                    <small>
                    • 调度器: ${details.scheduler_running ? '运行中' : '已停止'}<br>
                    • OCR服务: ${details.ocr_enabled ? '已启用' : '已禁用'}<br>
                    • 下次任务: ${details.next_run_time || '未设置'}
                    </small>
                `;
                showStatus(statusMsg, 'success');
            } catch (error) {
                showStatus('❌ 服务检查失败: ' + error.message, 'error');
            } finally {
                btn.disabled = false;
                btn.innerHTML = '检查服务状态';
            }
        }

        function highlightUrls(text) {
            // Convert URLs to clickable links
            const urlRegex = /(https?:\/\/[^\s]+)/g;
            return text.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
        }

        function formatLogLine(line) {
            line = highlightUrls(line);

            if (line.includes('ERROR') || line.includes('error')) {
                return '<div class="log-line log-error">' + line + '</div>';
            } else if (line.includes('WARNING') || line.includes('warning')) {
                return '<div class="log-line log-warning">' + line + '</div>';
            } else if (line.includes('INFO') || line.includes('Starting') || line.includes('success')) {
                return '<div class="log-line log-info">' + line + '</div>';
            }
            return '<div class="log-line">' + line + '</div>';
        }

        async function loadLogs() {
            const logContainer = document.getElementById('logContainer');
            logContainer.innerHTML = '<div class="loading"></div> 加载中...';

            try {
                const response = await fetch('/api/logs?lines=100');
                const data = await response.json();

                if (data.logs) {
                    const formattedLogs = data.logs
                        .split('\\n')
                        .map(line => formatLogLine(line))
                        .join('');

                    logContainer.innerHTML = formattedLogs || '暂无日志';

                    // Update stats
                    document.getElementById('logLines').textContent = data.total_lines;
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('zh-CN');

                    // Auto scroll to bottom
                    logContainer.scrollTop = logContainer.scrollHeight;
                } else {
                    logContainer.innerHTML = '暂无日志';
                }
            } catch (error) {
                logContainer.innerHTML = '❌ 加载日志失败: ' + error.message;
            }
        }

        function clearLogDisplay() {
            const logContainer = document.getElementById('logContainer');
            logContainer.innerHTML = '日志显示已清空，点击"刷新日志"重新加载...';
            document.getElementById('logLines').textContent = '0';
        }

        // Auto-load logs on page load
        window.addEventListener('load', () => {
            loadLogs();
            // Auto refresh every 30 seconds
            setInterval(() => loadLogs(), 30000);
        });
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 Daily News Service</h1>
            <p>手动推送每日新闻 & 查看服务日志</p>
        </div>

        <div class="card">
            <h2>🚀 手动推送</h2>
            <div class="button-group">
                <button id="triggerBtn" class="btn-primary" onclick="triggerNews()">
                    立即推送新闻
                </button>
                <button id="healthBtn" class="btn-success" onclick="checkHealth()">
                    检查服务状态
                </button>
            </div>
            <div id="statusBox" style="display: none;"></div>
        </div>

        <div class="card">
            <h2>📊 服务日志</h2>
            <div class="button-group">
                <button class="btn-secondary" onclick="loadLogs()">
                    刷新日志
                </button>
                <button class="btn-secondary" onclick="clearLogDisplay()">
                    清空显示
                </button>
            </div>
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="logLines">0</div>
                    <div class="stat-label">日志行数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="lastUpdate">-</div>
                    <div class="stat-label">最后更新</div>
                </div>
            </div>
            <div id="logContainer" class="log-container">
                点击"刷新日志"查看最新日志...
            </div>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/trigger", response_model=TriggerResponse)
async def trigger_manual_send():
    """Manually trigger news sending"""
    try:
        logger.info("Manual trigger requested via web API")
        scheduler = get_scheduler()

        # Run the task asynchronously
        await scheduler.run_once()

        return TriggerResponse(
            success=True,
            message="新闻推送任务已成功执行"
        )
    except Exception as e:
        logger.error(f"Manual trigger failed: {str(e)}", exc_info=True)
        return TriggerResponse(
            success=False,
            message=f"推送失败: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        scheduler = get_scheduler()

        # Get next run time if scheduled
        next_run_time = None
        if scheduler.scheduler.running:
            jobs = scheduler.scheduler.get_jobs()
            if jobs:
                next_run_time = jobs[0].next_run_time.strftime("%Y-%m-%d %H:%M:%S") if jobs[0].next_run_time else None

        return {
            "status": "healthy",
            "details": {
                "scheduler_running": scheduler.scheduler.running,
                "ocr_enabled": scheduler.use_ocr,
                "next_run_time": next_run_time
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs", response_model=LogResponse)
async def get_logs(lines: int = 100):
    """Get service logs"""
    try:
        log_file = Path("/app/logs/daily_news.log")

        # Try multiple log file locations
        if not log_file.exists():
            log_file = Path("daily_news.log")
        if not log_file.exists():
            log_file = Path("logs/daily_news.log")

        if log_file.exists() and log_file.stat().st_size > 0:
            # Read last N lines
            with open(log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

            return LogResponse(
                logs=''.join(last_lines),
                total_lines=len(last_lines)
            )

        # If no logs available
        return LogResponse(
            logs="暂无日志（请触发一次推送以生成日志）",
            total_lines=0
        )

    except Exception as e:
        logger.error(f"Failed to read logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取日志失败: {str(e)}")
