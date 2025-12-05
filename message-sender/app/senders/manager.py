"""Message sender manager"""
from typing import Dict, Any, List, Optional
import logging
from .base import BaseSender
from .wecom import WeComSender
from .dingtalk import DingTalkSender
from .feishu import FeishuSender

logger = logging.getLogger(__name__)


class MessageSenderManager:
    """Manages multiple message senders"""

    SENDER_CLASSES = {
        "wecom": WeComSender,
        "dingtalk": DingTalkSender,
        "feishu": FeishuSender,
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize message sender manager

        Args:
            config: Configuration dictionary with senders config
        """
        self.senders: List[BaseSender] = []
        self._initialize_senders(config.get("senders", {}))

    def _initialize_senders(self, senders_config: Dict[str, Any]):
        """Initialize all configured senders"""
        for sender_type, sender_config in senders_config.items():
            if sender_type not in self.SENDER_CLASSES:
                logger.warning(f"Unknown sender type: {sender_type}")
                continue

            if not sender_config.get("enabled", True):
                logger.info(f"Sender {sender_type} is disabled")
                continue

            try:
                sender_class = self.SENDER_CLASSES[sender_type]
                sender = sender_class(sender_config)

                if sender.validate_config():
                    self.senders.append(sender)
                    logger.info(f"Initialized sender: {sender_type}")
                else:
                    logger.error(f"Invalid configuration for sender: {sender_type}")
            except Exception as e:
                logger.error(f"Failed to initialize sender {sender_type}: {str(e)}")

    async def send_to_all(
        self,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Send message to all enabled senders

        Args:
            title: Message title
            content: Message content
            message_type: Type of message
            extra: Extra parameters

        Returns:
            List of results from all senders
        """
        results = []
        for sender in self.senders:
            try:
                result = await sender.send(title, content, message_type, extra)
                results.append({
                    "sender": sender.__class__.__name__,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error sending via {sender.__class__.__name__}: {str(e)}")
                results.append({
                    "sender": sender.__class__.__name__,
                    "result": {"success": False, "error": str(e)}
                })

        return results

    async def send_to_specific(
        self,
        sender_type: str,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send message to a specific sender

        Args:
            sender_type: Type of sender (wecom, dingtalk, feishu)
            title: Message title
            content: Message content
            message_type: Type of message
            extra: Extra parameters

        Returns:
            Result from the sender
        """
        sender_class_name = self.SENDER_CLASSES.get(sender_type).__name__ if sender_type in self.SENDER_CLASSES else None

        if not sender_class_name:
            return {"success": False, "error": f"Unknown sender type: {sender_type}"}

        for sender in self.senders:
            if sender.__class__.__name__ == sender_class_name:
                try:
                    return await sender.send(title, content, message_type, extra)
                except Exception as e:
                    logger.error(f"Error sending via {sender_type}: {str(e)}")
                    return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Sender {sender_type} not configured or enabled"}

    def get_available_senders(self) -> List[str]:
        """Get list of available sender types"""
        return [sender.__class__.__name__ for sender in self.senders]
