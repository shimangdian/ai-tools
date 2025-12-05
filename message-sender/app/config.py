"""Configuration management"""
import os
import yaml
from typing import Dict, Any
from pathlib import Path


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

    # Override with environment variables if set
    senders = config.get("senders", {})

    # WeCom configuration
    if os.getenv("WECOM_WEBHOOK_URL"):
        senders["wecom"] = {
            "enabled": os.getenv("WECOM_ENABLED", "true").lower() == "true",
            "webhook_url": os.getenv("WECOM_WEBHOOK_URL"),
            "mentioned_list": os.getenv("WECOM_MENTIONED_LIST", "").split(",") if os.getenv("WECOM_MENTIONED_LIST") else [],
            "mentioned_mobile_list": os.getenv("WECOM_MENTIONED_MOBILE_LIST", "").split(",") if os.getenv("WECOM_MENTIONED_MOBILE_LIST") else [],
        }

    # DingTalk configuration
    if os.getenv("DINGTALK_WEBHOOK_URL"):
        senders["dingtalk"] = {
            "enabled": os.getenv("DINGTALK_ENABLED", "true").lower() == "true",
            "webhook_url": os.getenv("DINGTALK_WEBHOOK_URL"),
            "secret": os.getenv("DINGTALK_SECRET", ""),
            "at_mobiles": os.getenv("DINGTALK_AT_MOBILES", "").split(",") if os.getenv("DINGTALK_AT_MOBILES") else [],
            "at_all": os.getenv("DINGTALK_AT_ALL", "false").lower() == "true",
        }

    # Feishu configuration
    if os.getenv("FEISHU_WEBHOOK_URL"):
        senders["feishu"] = {
            "enabled": os.getenv("FEISHU_ENABLED", "true").lower() == "true",
            "webhook_url": os.getenv("FEISHU_WEBHOOK_URL"),
            "secret": os.getenv("FEISHU_SECRET", ""),
        }

    config["senders"] = senders

    # API configuration
    config["api"] = {
        "host": os.getenv("API_HOST", config.get("api", {}).get("host", "0.0.0.0")),
        "port": int(os.getenv("API_PORT", config.get("api", {}).get("port", 8000))),
        "api_key": os.getenv("API_KEY", config.get("api", {}).get("api_key", "")),
    }

    return config
