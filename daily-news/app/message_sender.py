"""Message sender client"""
import logging
from typing import Optional, Dict, Any
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)


class MessageSender:
    """Client for message sender service"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize message sender client

        Args:
            base_url: Base URL of message sender service
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def send_message(
        self,
        title: str,
        content: str,
        message_type: str = "markdown_v2",
        sender_type: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send a message via message sender service

        Args:
            title: Message title
            content: Message content
            message_type: Message type (text, markdown)
            sender_type: Specific sender type (wecom, dingtalk, feishu)
            extra: Extra parameters

        Returns:
            Response from message sender service
        """
        url = f"{self.base_url}/send"
        payload = {
            "title": title,
            "content": content,
            "message_type": message_type,
        }

        if sender_type:
            payload["sender_type"] = sender_type

        if extra:
            payload["extra"] = extra

        try:
            logger.info(f"Sending message to {url}: {title}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=30
                ) as response:
                    result = await response.json()

                    if response.status == 200 and result.get("success"):
                        logger.info(f"Message sent successfully: {title}")
                        return {"success": True, "data": result}
                    else:
                        error_msg = result.get("message", "Unknown error")
                        logger.error(f"Failed to send message: {error_msg}")
                        return {"success": False, "error": error_msg, "data": result}

        except aiohttp.ClientError as e:
            logger.error(f"Network error sending message: {str(e)}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error sending message: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def create_text_message_from_ocr(self, ocr_text: str, date: Optional[str] = None) -> tuple:
        """
        Create text message from OCR extracted text

        Args:
            ocr_text: Text extracted from image via OCR
            date: Date string, defaults to today

        Returns:
            Tuple of (title, content) for text message
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        title = f"📰 每日早报 - {date}"
        content = f"{ocr_text}\n\n---\n每日 8 点自动推送 | 图片转文字版"

        return title, content

    def create_wecom_markdown_v2_message(self, image_url: str, date: Optional[str] = None) -> tuple:
        """
        Create WeCom markdown_v2 format message for daily news

        Args:
            image_url: URL of the news image
            date: Date string, defaults to today

        Returns:
            Tuple of (title, content) for markdown_v2 message
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        title = f"📰 每日早报 - {date}"

        # markdown_v2 supports images with ![](url) syntax
        content = f"""# 📰 每日早报

**日期**: {date}

![早报图片]({image_url})

---
*每日 8 点自动推送*"""

        return title, content

    async def send_daily_news(self, image_url: str) -> Dict[str, Any]:
        """
        Send daily news to WeCom using markdown_v2 type (displays image)

        Args:
            image_url: URL of the news image

        Returns:
            Response from message sender service
        """
        title, content = self.create_wecom_markdown_v2_message(image_url)

        # Send to WeCom specifically using markdown_v2 type to display image
        result = await self.send_message(
            title=title,
            content=content,
            message_type="markdown_v2",
            sender_type="wecom"
        )

        return result
