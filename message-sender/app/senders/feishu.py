"""Feishu (Lark) message sender"""
from typing import Dict, Any, Optional
import aiohttp
import time
import hmac
import hashlib
import base64
from .base import BaseSender


class FeishuSender(BaseSender):
    """Feishu (Lark) message sender"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.secret = config.get("secret", "")

    def validate_config(self) -> bool:
        """Validate Feishu configuration"""
        if not self.webhook_url:
            self.logger.error("Feishu webhook_url is required")
            return False
        if not self.webhook_url.startswith("https://open.feishu.cn/open-apis/bot/v2/hook/"):
            self.logger.error("Invalid Feishu webhook_url format")
            return False
        return True

    def _generate_sign(self, timestamp: int) -> str:
        """Generate signature for Feishu webhook"""
        if not self.secret:
            return ""

        string_to_sign = f"{timestamp}\n{self.secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    async def send(
        self,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send message via Feishu webhook

        Args:
            title: Message title
            content: Message content
            message_type: Type of message (text, post, interactive)
            extra: Extra parameters

        Returns:
            Dict containing success status and response data
        """
        if not self.is_enabled():
            return {"success": False, "error": "Sender is disabled"}

        if not self.validate_config():
            return {"success": False, "error": "Invalid configuration"}

        try:
            payload = {
                "msg_type": "text",
                "content": {
                    "text": f"{title}\n{content}"
                }
            }

            # Add signature if secret is configured
            if self.secret:
                timestamp = int(time.time())
                sign = self._generate_sign(timestamp)
                payload["timestamp"] = str(timestamp)
                payload["sign"] = sign

            # Support for rich text (post type)
            if message_type == "post":
                payload = {
                    "msg_type": "post",
                    "content": {
                        "post": {
                            "zh_cn": {
                                "title": title,
                                "content": [
                                    [
                                        {
                                            "tag": "text",
                                            "text": content
                                        }
                                    ]
                                ]
                            }
                        }
                    }
                }
                if self.secret:
                    timestamp = int(time.time())
                    sign = self._generate_sign(timestamp)
                    payload["timestamp"] = str(timestamp)
                    payload["sign"] = sign

            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload, timeout=10) as response:
                    result = await response.json()

                    if result.get("code") == 0:
                        self.logger.info(f"Message sent successfully via Feishu: {title}")
                        return {"success": True, "response": result}
                    else:
                        error_msg = result.get("msg", "Unknown error")
                        self.logger.error(f"Failed to send Feishu message: {error_msg}")
                        return {"success": False, "error": error_msg, "response": result}

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error sending Feishu message: {str(e)}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Unexpected error sending Feishu message: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
