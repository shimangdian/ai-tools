from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImageBase(BaseModel):
    """图片基础模型"""
    file_path: str
    file_name: str
    file_size: int
    width: Optional[int] = None
    height: Optional[int] = None


class ImageCreate(ImageBase):
    """创建图片记录"""
    hash_value: str
    modified_at: Optional[datetime] = None


class ImageResponse(ImageBase):
    """图片响应模型"""
    id: int
    hash_value: str
    created_at: datetime
    modified_at: Optional[datetime] = None
    scanned_at: datetime

    class Config:
        from_attributes = True


class SimilarGroup(BaseModel):
    """相似图片组"""
    group_id: int
    images: List[ImageResponse]
    similarity_scores: Optional[dict] = None  # 图片间的相似度分数


class ScanRequest(BaseModel):
    """扫描请求"""
    scan_dir: Optional[str] = None  # 可选，默认使用配置的目录
    recursive: bool = True
    threshold: int = 10


class ScanResponse(BaseModel):
    """扫描响应"""
    task_id: int
    status: str
    message: str


class ScanProgress(BaseModel):
    """扫描进度"""
    task_id: int
    status: str
    total_files: int
    processed_files: int
    similar_groups: int
    progress_percent: float


class DeleteRequest(BaseModel):
    """删除请求"""
    file_paths: List[str]


class DeleteResponse(BaseModel):
    """删除响应"""
    success: bool
    deleted_count: int
    failed_files: List[str] = []
    message: str


class RestoreRequest(BaseModel):
    """恢复请求"""
    file_paths: List[str]


class RestoreResponse(BaseModel):
    """恢复响应"""
    success: bool
    restored_count: int
    failed_files: List[str] = []
    message: str
