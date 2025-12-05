"""Base sender interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseSender(ABC):
    """Base class for all message senders"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize sender with configuration

        Args:
            config: Configuration dictionary for the sender
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def send(
        self,
        title: str,
        content: str,
        message_type: str = "text",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Send a message

        Args:
            title: Message title
            content: Message content
            message_type: Type of message (text, markdown, etc.)
            extra: Extra parameters specific to the sender

        Returns:
            Dict containing success status and response data
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate sender configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        pass

    def is_enabled(self) -> bool:
        """Check if sender is enabled"""
        return self.enabled
