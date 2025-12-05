"""WeCom (Enterprise WeChat) message sender"""
from typing import Dict, Any, Optional
import aiohttp
from .base import BaseSender


class WeComSender(BaseSender):
    """WeCom (Enterprise WeChat) message sender"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.mentioned_list = config.get("mentioned_list", [])
        self.mentioned_mobile_list = config.get("mentioned_mobile_list", [])

    def validate_config(self) -> bool:
        """Validate WeCom configuration"""
        if not self.webhook_url:
            self.logger.error("WeCom webhook_url is required")
            return False
        if not self.webhook_url.startswith("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="):
            self.logger.error("Invalid WeCom webhook_url format")
            return False
        return True

    async def send(
        self,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send message via WeCom webhook

        Args:
            title: Message title (used in markdown/news type)
            content: Message content (for text/markdown) or image URL (for image/news)
            message_type: Type of message (text, markdown, image, news)
            extra: Extra parameters (mentioned_list, mentioned_mobile_list, description, url, picurl)

        Returns:
            Dict containing success status and response data
        """
        if not self.is_enabled():
            return {"success": False, "error": "Sender is disabled"}

        if not self.validate_config():
            return {"success": False, "error": "Invalid configuration"}

        extra = extra or {}
        mentioned_list = extra.get("mentioned_list", self.mentioned_list)
        mentioned_mobile_list = extra.get("mentioned_mobile_list", self.mentioned_mobile_list)

        try:
            if message_type == "markdown":
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": f"**{title}**\n\n{content}"
                    }
                }
            elif message_type == "markdown_v2":
                # markdown_v2 supports images, tables, and more formatting
                payload = {
                    "msgtype": "markdown_v2",
                    "markdown_v2": {
                        "content": content  # Use content directly, should include title if needed
                    }
                }
            elif message_type == "image":
                # Image type - content should be base64 encoded image or use picurl in extra
                # Note: Webhook only supports picurl via news type, not direct image type
                # So we'll create a simple news with just image
                image_url = extra.get("picurl", content)
                payload = {
                    "msgtype": "news",
                    "news": {
                        "articles": [
                            {
                                "title": title,
                                "description": extra.get("description", ""),
                                "url": extra.get("url", image_url),
                                "picurl": image_url
                            }
                        ]
                    }
                }
            elif message_type == "news":
                # News type - for rich content with image
                image_url = extra.get("picurl", content)
                payload = {
                    "msgtype": "news",
                    "news": {
                        "articles": [
                            {
                                "title": title,
                                "description": extra.get("description", "点击查看详情"),
                                "url": extra.get("url", image_url),
                                "picurl": image_url
                            }
                        ]
                    }
                }
            else:  # text
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": f"{title}\n{content}",
                        "mentioned_list": mentioned_list,
                        "mentioned_mobile_list": mentioned_mobile_list,
                    }
                }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload, timeout=10) as response:
                    result = await response.json()

                    if result.get("errcode") == 0:
                        self.logger.info(f"Message sent successfully via WeCom: {title}")
                        return {"success": True, "response": result}
                    else:
                        error_msg = result.get("errmsg", "Unknown error")
                        self.logger.error(f"Failed to send WeCom message: {error_msg}")
                        return {"success": False, "error": error_msg, "response": result}

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error sending WeCom message: {str(e)}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Unexpected error sending WeCom message: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
