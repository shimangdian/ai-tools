from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    app_name: str = "Photo Clean"
    app_version: str = "1.0.0"

    # 路径配置
    photo_dir: str = os.getenv("PHOTO_DIR", "/data/photo")
    trash_dir: str = os.getenv("TRASH_DIR", "/data/trash")
    db_path: str = os.getenv("DB_PATH", "/data/db/photo_clean.db")

    # 算法配置
    similarity_threshold: int = int(os.getenv("SIMILARITY_THRESHOLD", "10"))
    scan_workers: int = int(os.getenv("SCAN_WORKERS", "4"))

    # 回收站配置
    trash_retention_days: int = int(os.getenv("TRASH_RETENTION_DAYS", "30"))

    # 支持的图片格式
    supported_formats: tuple = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')

    class Config:
        env_file = ".env"


settings = Settings()
