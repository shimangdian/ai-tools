"""Daily News Service - Main Entry Point"""
import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from .config import load_config
from .news_fetcher import NewsFetcher
from .message_sender import MessageSender
from .scheduler import DailyNewsScheduler

# Ensure logs directory exists
log_dir = Path("/app/logs")
if not log_dir.exists():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

log_file = log_dir / "daily_news.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger(__name__)


class DailyNewsService:
    """Daily News Service"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize service

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.scheduler: Optional[DailyNewsScheduler] = None
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        if self.scheduler:
            self.scheduler.shutdown()
        sys.exit(0)

    def initialize(self):
        """Initialize service components"""
        logger.info("Initializing Daily News Service...")

        # Initialize news fetcher
        news_api_url = self.config["news"]["api_url"]
        news_fetcher = NewsFetcher(news_api_url)
        logger.info(f"News fetcher initialized with URL: {news_api_url}")

        # Initialize message sender
        sender_config = self.config["message_sender"]
        message_sender = MessageSender(
            base_url=sender_config["base_url"],
            api_key=sender_config.get("api_key")
        )
        logger.info(f"Message sender initialized with URL: {sender_config['base_url']}")

        # Initialize scheduler
        schedule_config = self.config["schedule"]
        ocr_config = self.config.get("ocr", {})
        self.scheduler = DailyNewsScheduler(
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
            self.scheduler.schedule_daily_task(
                hour=schedule_config["hour"],
                minute=schedule_config["minute"]
            )
            logger.info(
                f"Daily task scheduled at {schedule_config['hour']:02d}:{schedule_config['minute']:02d} "
                f"{schedule_config['timezone']}"
            )
        else:
            logger.info("Scheduler is disabled in configuration")

    async def run_once(self):
        """Run the task once immediately"""
        if not self.scheduler:
            self.initialize()
        await self.scheduler.run_once()

    def start(self):
        """Start the service"""
        try:
            self.initialize()
            self.scheduler.start()

            logger.info("Daily News Service started successfully")
            logger.info("Press Ctrl+C to stop the service")

            # Keep the service running
            try:
                asyncio.get_event_loop().run_forever()
            except (KeyboardInterrupt, SystemExit):
                logger.info("Service interrupted")

        except Exception as e:
            logger.error(f"Error starting service: {str(e)}", exc_info=True)
            sys.exit(1)

        finally:
            if self.scheduler:
                self.scheduler.shutdown()
            logger.info("Service stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Daily News Service")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
        default=None
    )
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Run the task once immediately and exit"
    )

    args = parser.parse_args()

    service = DailyNewsService(config_path=args.config)

    if args.run_once:
        logger.info("Running task once...")
        asyncio.run(service.run_once())
    else:
        service.start()


if __name__ == "__main__":
    main()
