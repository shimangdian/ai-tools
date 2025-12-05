"""DingTalk message sender"""
from typing import Dict, Any, Optional
import aiohttp
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
from .base import BaseSender


class DingTalkSender(BaseSender):
    """DingTalk message sender"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.webhook_url = config.get("webhook_url", "")
        self.secret = config.get("secret", "")
        self.at_mobiles = config.get("at_mobiles", [])
        self.at_all = config.get("at_all", False)

    def validate_config(self) -> bool:
        """Validate DingTalk configuration"""
        if not self.webhook_url:
            self.logger.error("DingTalk webhook_url is required")
            return False
        if not self.webhook_url.startswith("https://oapi.dingtalk.com/robot/send?access_token="):
            self.logger.error("Invalid DingTalk webhook_url format")
            return False
        return True

    def _generate_sign(self) -> tuple:
        """Generate signature for DingTalk webhook"""
        if not self.secret:
            return None, None

        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    async def send(
        self,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send message via DingTalk webhook

        Args:
            title: Message title
            content: Message content
            message_type: Type of message (text, markdown)
            extra: Extra parameters (at_mobiles, at_all)

        Returns:
            Dict containing success status and response data
        """
        if not self.is_enabled():
            return {"success": False, "error": "Sender is disabled"}

        if not self.validate_config():
            return {"success": False, "error": "Invalid configuration"}

        extra = extra or {}
        at_mobiles = extra.get("at_mobiles", self.at_mobiles)
        at_all = extra.get("at_all", self.at_all)

        try:
            url = self.webhook_url
            timestamp, sign = self._generate_sign()
            if timestamp and sign:
                url = f"{url}&timestamp={timestamp}&sign={sign}"

            if message_type == "markdown":
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": title,
                        "text": content
                    },
                    "at": {
                        "atMobiles": at_mobiles,
                        "isAtAll": at_all
                    }
                }
            else:  # text
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": f"{title}\n{content}"
                    },
                    "at": {
                        "atMobiles": at_mobiles,
                        "isAtAll": at_all
                    }
                }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    result = await response.json()

                    if result.get("errcode") == 0:
                        self.logger.info(f"Message sent successfully via DingTalk: {title}")
                        return {"success": True, "response": result}
                    else:
                        error_msg = result.get("errmsg", "Unknown error")
                        self.logger.error(f"Failed to send DingTalk message: {error_msg}")
                        return {"success": False, "error": error_msg, "response": result}

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error sending DingTalk message: {str(e)}")
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            self.logger.error(f"Unexpected error sending DingTalk message: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
