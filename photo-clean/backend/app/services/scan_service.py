from sqlalchemy.orm import Session
from app.database import ImageRecord, ScanTask
from app.core.scanner import scan_directory, get_file_info
from app.core.hash import get_image_hash, get_image_info
from app.core.similarity import find_similar_groups
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


def process_single_image(file_path: str) -> Dict:
    """处理单个图片文件（用于多进程）"""
    try:
        # 获取文件信息
        file_info = get_file_info(file_path)

        # 计算哈希
        hash_value = get_image_hash(file_path)
        if not hash_value:
            return None

        # 获取图片信息
        img_info = get_image_info(file_path)
        if not img_info:
            return None

        return {
            "file_path": file_path,
            "file_name": file_info["name"],
            "file_size": file_info["size"],
            "width": img_info["width"],
            "height": img_info["height"],
            "hash_value": hash_value,
            "modified_at": datetime.fromtimestamp(file_info["modified_at"])
        }
    except Exception as e:
        logger.error(f"处理图片失败: {file_path}, 错误: {e}")
        return None


class ScanService:
    """扫描服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_scan_task(self, scan_dir: str) -> ScanTask:
        """创建扫描任务"""
        task = ScanTask(
            scan_dir=scan_dir,
            status="pending",
            started_at=datetime.utcnow()
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task_status(self, task_id: int, status: str, **kwargs):
        """更新任务状态"""
        task = self.db.query(ScanTask).filter(ScanTask.id == task_id).first()
        if task:
            task.status = status
            for key, value in kwargs.items():
                setattr(task, key, value)
            self.db.commit()

    def scan_and_process(
        self,
        task_id: int,
        scan_dir: str,
        recursive: bool = True,
        threshold: int = 10,
        workers: int = 4
    ) -> Dict:
        """
        扫描并处理图片

        Args:
            task_id: 任务ID
            scan_dir: 扫描目录
            recursive: 是否递归
            threshold: 相似度阈值
            workers: 工作进程数

        Returns:
            处理结果字典
        """
        try:
            # 更新任务状态
            self.update_task_status(task_id, "running")

            # 扫描目录
            logger.info(f"开始扫描目录: {scan_dir}")
            image_files = scan_directory(scan_dir, recursive)

            if not image_files:
                self.update_task_status(
                    task_id,
                    "completed",
                    total_files=0,
                    processed_files=0,
                    completed_at=datetime.utcnow()
                )
                return {"groups": [], "total_files": 0}

            total_files = len(image_files)
            self.update_task_status(task_id, "running", total_files=total_files)

            # 多进程处理图片
            logger.info(f"开始处理 {total_files} 个图片文件，使用 {workers} 个进程")
            processed_count = 0
            image_hashes = {}

            with ProcessPoolExecutor(max_workers=workers) as executor:
                future_to_path = {
                    executor.submit(process_single_image, path): path
                    for path in image_files
                }

                for future in as_completed(future_to_path):
                    result = future.result()
                    if result:
                        # 保存到数据库
                        self._save_or_update_image(result)
                        image_hashes[result["file_path"]] = result["hash_value"]

                    processed_count += 1

                    # 更新进度
                    if processed_count % 100 == 0 or processed_count == total_files:
                        self.update_task_status(
                            task_id,
                            "running",
                            processed_files=processed_count
                        )
                        logger.info(f"处理进度: {processed_count}/{total_files}")

            # 查找相似图片组
            logger.info("开始查找相似图片组")
            groups = find_similar_groups(image_hashes, threshold)

            # 完成任务
            self.update_task_status(
                task_id,
                "completed",
                processed_files=processed_count,
                similar_groups=len(groups),
                completed_at=datetime.utcnow()
            )

            return {
                "groups": groups,
                "total_files": processed_count,
                "similar_groups": len(groups)
            }

        except Exception as e:
            logger.error(f"扫描任务失败: {e}")
            self.update_task_status(task_id, "failed", completed_at=datetime.utcnow())
            raise

    def _save_or_update_image(self, image_data: Dict):
        """保存或更新图片记录"""
        existing = self.db.query(ImageRecord).filter(
            ImageRecord.file_path == image_data["file_path"]
        ).first()

        if existing:
            # 更新现有记录
            for key, value in image_data.items():
                setattr(existing, key, value)
            existing.scanned_at = datetime.utcnow()
        else:
            # 创建新记录
            image = ImageRecord(**image_data)
            self.db.add(image)

        self.db.commit()

    def get_task_progress(self, task_id: int) -> Dict:
        """获取任务进度"""
        task = self.db.query(ScanTask).filter(ScanTask.id == task_id).first()
        if not task:
            return None

        progress = 0
        if task.total_files > 0:
            progress = (task.processed_files / task.total_files) * 100

        return {
            "task_id": task.id,
            "status": task.status,
            "total_files": task.total_files,
            "processed_files": task.processed_files,
            "similar_groups": task.similar_groups,
            "progress_percent": round(progress, 2)
        }

    def get_similar_groups(self, task_id: int) -> List[Dict]:
        """获取相似图片组"""
        # 从数据库获取所有图片记录
        images = self.db.query(ImageRecord).all()

        if not images:
            return []

        # 构建哈希映射
        image_hashes = {img.file_path: img.hash_value for img in images if img.hash_value}

        # 查找相似组
        groups = find_similar_groups(image_hashes, threshold=10)

        # 构建返回数据
        result = []
        for i, group in enumerate(groups):
            group_images = []
            for path in group:
                img = self.db.query(ImageRecord).filter(
                    ImageRecord.file_path == path
                ).first()
                if img:
                    group_images.append({
                        "id": img.id,
                        "file_path": img.file_path,
                        "file_name": img.file_name,
                        "file_size": img.file_size,
                        "width": img.width,
                        "height": img.height,
                        "hash_value": img.hash_value,
                        "modified_at": img.modified_at.isoformat() if img.modified_at else None
                    })

            result.append({
                "group_id": i + 1,
                "images": group_images
            })

        return result
