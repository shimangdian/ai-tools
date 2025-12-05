"""Configuration management"""
import os
import yaml
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file or environment variables

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = os.getenv("CONFIG_PATH", "config.yaml")

    config = {}

    # Load from YAML file if exists
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}

    # Override with environment variables
    config.setdefault("news", {})
    config["news"]["api_url"] = os.getenv("NEWS_API_URL", config.get("news", {}).get("api_url", "https://dwz.2xb.cn/zaob"))

    # Message sender configuration
    config.setdefault("message_sender", {})
    config["message_sender"]["base_url"] = os.getenv(
        "MESSAGE_SENDER_URL",
        config.get("message_sender", {}).get("base_url", "http://localhost:8000")
    )
    config["message_sender"]["api_key"] = os.getenv(
        "MESSAGE_SENDER_API_KEY",
        config.get("message_sender", {}).get("api_key", "")
    )

    # Schedule configuration
    config.setdefault("schedule", {})
    config["schedule"]["enabled"] = os.getenv(
        "SCHEDULE_ENABLED",
        str(config.get("schedule", {}).get("enabled", True))
    ).lower() == "true"
    config["schedule"]["hour"] = int(os.getenv(
        "SCHEDULE_HOUR",
        str(config.get("schedule", {}).get("hour", 8))
    ))
    config["schedule"]["minute"] = int(os.getenv(
        "SCHEDULE_MINUTE",
        str(config.get("schedule", {}).get("minute", 0))
    ))
    config["schedule"]["timezone"] = os.getenv(
        "SCHEDULE_TIMEZONE",
        config.get("schedule", {}).get("timezone", "Asia/Shanghai")
    )

    # OCR configuration
    config.setdefault("ocr", {})
    config["ocr"]["enabled"] = os.getenv(
        "OCR_ENABLED",
        str(config.get("ocr", {}).get("enabled", True))
    ).lower() == "true"

    return config
