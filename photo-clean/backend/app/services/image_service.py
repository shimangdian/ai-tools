from sqlalchemy.orm import Session
from app.database import ImageRecord, OperationLog
from app.config import settings
from typing import List, Dict
from datetime import datetime, timedelta
import shutil
import os
import logging

logger = logging.getLogger(__name__)


class ImageService:
    """图片操作服务"""

    def __init__(self, db: Session):
        self.db = db

    def delete_images(self, file_paths: List[str]) -> Dict:
        """
        删除图片（移动到回收站）

        Args:
            file_paths: 要删除的文件路径列表

        Returns:
            删除结果
        """
        # 确保回收站目录存在
        os.makedirs(settings.trash_dir, exist_ok=True)

        deleted_count = 0
        failed_files = []

        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    failed_files.append(f"{file_path} (文件不存在)")
                    continue

                # 生成回收站路径
                # 使用文件名和时间戳避免冲突
                filename = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                trash_filename = f"{timestamp}_{filename}"
                trash_path = os.path.join(settings.trash_dir, trash_filename)

                # 移动文件到回收站
                shutil.move(file_path, trash_path)

                # 记录操作日志
                log = OperationLog(
                    operation_type="delete",
                    file_path=file_path,
                    trash_path=trash_path,
                    created_at=datetime.utcnow()
                )
                self.db.add(log)

                deleted_count += 1
                logger.info(f"文件已移动到回收站: {file_path} -> {trash_path}")

            except Exception as e:
                logger.error(f"删除文件失败: {file_path}, 错误: {e}")
                failed_files.append(f"{file_path} ({str(e)})")

        self.db.commit()

        return {
            "success": deleted_count > 0,
            "deleted_count": deleted_count,
            "failed_files": failed_files,
            "message": f"成功删除 {deleted_count} 个文件，失败 {len(failed_files)} 个"
        }

    def restore_images(self, file_paths: List[str]) -> Dict:
        """
        从回收站恢复图片

        Args:
            file_paths: 原始文件路径列表

        Returns:
            恢复结果
        """
        restored_count = 0
        failed_files = []

        for file_path in file_paths:
            try:
                # 查找删除记录
                log = self.db.query(OperationLog).filter(
                    OperationLog.file_path == file_path,
                    OperationLog.operation_type == "delete",
                    OperationLog.is_permanent == False
                ).order_by(OperationLog.created_at.desc()).first()

                if not log:
                    failed_files.append(f"{file_path} (未找到删除记录)")
                    continue

                if not os.path.exists(log.trash_path):
                    failed_files.append(f"{file_path} (回收站中不存在)")
                    continue

                # 确保原目录存在
                original_dir = os.path.dirname(file_path)
                os.makedirs(original_dir, exist_ok=True)

                # 恢复文件
                shutil.move(log.trash_path, file_path)

                # 记录恢复操作
                restore_log = OperationLog(
                    operation_type="restore",
                    file_path=file_path,
                    trash_path=log.trash_path,
                    created_at=datetime.utcnow()
                )
                self.db.add(restore_log)

                restored_count += 1
                logger.info(f"文件已恢复: {log.trash_path} -> {file_path}")

            except Exception as e:
                logger.error(f"恢复文件失败: {file_path}, 错误: {e}")
                failed_files.append(f"{file_path} ({str(e)})")

        self.db.commit()

        return {
            "success": restored_count > 0,
            "restored_count": restored_count,
            "failed_files": failed_files,
            "message": f"成功恢复 {restored_count} 个文件，失败 {len(failed_files)} 个"
        }

    def clean_trash(self) -> Dict:
        """
        清理回收站（删除超过保留期的文件）

        Returns:
            清理结果
        """
        cutoff_date = datetime.utcnow() - timedelta(days=settings.trash_retention_days)

        # 查找过期的删除记录
        expired_logs = self.db.query(OperationLog).filter(
            OperationLog.operation_type == "delete",
            OperationLog.is_permanent == False,
            OperationLog.created_at < cutoff_date
        ).all()

        deleted_count = 0
        failed_count = 0

        for log in expired_logs:
            try:
                if os.path.exists(log.trash_path):
                    os.remove(log.trash_path)
                    deleted_count += 1

                # 标记为永久删除
                log.is_permanent = True

            except Exception as e:
                logger.error(f"删除回收站文件失败: {log.trash_path}, 错误: {e}")
                failed_count += 1

        self.db.commit()

        return {
            "success": True,
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "message": f"清理完成，删除 {deleted_count} 个文件，失败 {failed_count} 个"
        }

    def get_trash_info(self) -> Dict:
        """
        获取回收站信息

        Returns:
            回收站统计信息
        """
        # 统计回收站文件
        active_logs = self.db.query(OperationLog).filter(
            OperationLog.operation_type == "delete",
            OperationLog.is_permanent == False
        ).all()

        total_size = 0
        file_count = len(active_logs)

        for log in active_logs:
            if os.path.exists(log.trash_path):
                total_size += os.path.getsize(log.trash_path)

        return {
            "file_count": file_count,
            "total_size": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "retention_days": settings.trash_retention_days
        }
