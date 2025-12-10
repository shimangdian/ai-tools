"""Scheduler for daily news task"""
import logging
import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .news_fetcher import NewsFetcher
from .message_sender import MessageSender
from .ocr_service import OCRService

logger = logging.getLogger(__name__)


class DailyNewsScheduler:
    """Scheduler for daily news task"""

    def __init__(
        self,
        news_fetcher: NewsFetcher,
        message_sender: MessageSender,
        timezone: str = "Asia/Shanghai",
        use_ocr: bool = True,
        max_image_side: int = 8000,
        ocr_api_url: Optional[str] = None,
        ocr_token: Optional[str] = None
    ):
        """
        Initialize scheduler

        Args:
            news_fetcher: News fetcher instance
            message_sender: Message sender instance
            timezone: Timezone for scheduling
            use_ocr: Whether to use OCR to extract text from image
            max_image_side: Maximum side length for OCR images
            ocr_api_url: OCR API URL (optional)
            ocr_token: OCR API Token (optional)
        """
        self.news_fetcher = news_fetcher
        self.message_sender = message_sender
        self.timezone = timezone
        self.use_ocr = use_ocr
        self.scheduler = AsyncIOScheduler(timezone=timezone)

        # Initialize OCR service if enabled
        self.ocr_service = OCRService(
            max_image_side=max_image_side,
            api_url=ocr_api_url,
            token=ocr_token
        ) if use_ocr else None
        if use_ocr:
            logger.info(f"OCR service enabled with custom OCR API")

    async def send_daily_news_task(self):
        """Task to fetch and send daily news"""
        try:
            logger.info("Starting daily news task...")

            # Fetch news image URL
            image_url = await self.news_fetcher.get_daily_news_image()

            if not image_url:
                logger.error("Failed to fetch daily news image URL")
                raise Exception("Failed to fetch daily news image URL")

            logger.info(f"Fetched news image URL: {image_url}")

            # Try OCR if enabled
            if self.use_ocr and self.ocr_service:
                logger.info("Attempting to extract text from image using OCR...")
                try:
                    ocr_text = await self.ocr_service.extract_text_from_url(image_url)

                    if ocr_text and len(ocr_text.strip()) > 10:
                        logger.info(f"OCR extracted {len(ocr_text)} characters")

                        # Create text message from OCR result
                        title, content = self.message_sender.create_text_message_from_ocr(ocr_text)

                        # Send as text message
                        result = await self.message_sender.send_message(
                            title=title,
                            content=content,
                            message_type="text",
                            sender_type="wecom"
                        )

                        if result.get("success"):
                            logger.info("Daily news sent successfully via OCR text")
                            return
                        else:
                            error_msg = result.get('error', 'Unknown error')
                            logger.warning(f"Failed to send OCR text: {error_msg}")
                            # Don't raise here, try image fallback
                    else:
                        logger.warning("OCR result is empty or too short, falling back to image")

                except Exception as e:
                    logger.error(f"OCR failed: {str(e)}, falling back to image")

            # Fallback: Send with image URL (markdown_v2)
            logger.info("Sending news with image URL (markdown_v2)")
            result = await self.message_sender.send_daily_news(image_url)

            if result.get("success"):
                logger.info("Daily news sent successfully")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Failed to send daily news: {error_msg}")
                raise Exception(f"Failed to send daily news: {error_msg}")

        except Exception as e:
            logger.error(f"Error in daily news task: {str(e)}", exc_info=True)
            raise  # Re-raise to let caller know it failed

    def schedule_daily_task(self, hour: int = 8, minute: int = 0):
        """
        Schedule daily news task

        Args:
            hour: Hour to run task (0-23)
            minute: Minute to run task (0-59)
        """
        # Create cron trigger for daily execution
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone=self.timezone
        )

        self.scheduler.add_job(
            self.send_daily_news_task,
            trigger=trigger,
            id="daily_news_task",
            name="Daily News Task",
            replace_existing=True
        )

        logger.info(f"Scheduled daily news task at {hour:02d}:{minute:02d} {self.timezone}")

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

    async def run_once(self):
        """Run the task once immediately (for testing)"""
        logger.info("Running daily news task once...")
        await self.send_daily_news_task()
