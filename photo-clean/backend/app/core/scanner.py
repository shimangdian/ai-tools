import os
from typing import List, Callable, Optional
from pathlib import Path
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def is_image_file(file_path: str) -> bool:
    """
    判断文件是否为支持的图片格式

    Args:
        file_path: 文件路径

    Returns:
        是否为图片文件
    """
    return file_path.lower().endswith(settings.supported_formats)


def scan_directory(
    directory: str,
    recursive: bool = True,
    progress_callback: Optional[Callable[[int], None]] = None
) -> List[str]:
    """
    扫描目录下的所有图片文件

    Args:
        directory: 要扫描的目录路径
        recursive: 是否递归扫描子目录
        progress_callback: 进度回调函数，接收已扫描文件数

    Returns:
        图片文件路径列表
    """
    image_files = []
    directory_path = Path(directory)

    if not directory_path.exists():
        logger.error(f"目录不存在: {directory}")
        return []

    if not directory_path.is_dir():
        logger.error(f"路径不是目录: {directory}")
        return []

    logger.info(f"开始扫描目录: {directory}, 递归: {recursive}")

    try:
        if recursive:
            # 递归扫描所有子目录
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if is_image_file(file_path):
                        image_files.append(file_path)

                        if progress_callback:
                            progress_callback(len(image_files))
        else:
            # 只扫描当前目录
            for file in directory_path.iterdir():
                if file.is_file() and is_image_file(str(file)):
                    image_files.append(str(file))

                    if progress_callback:
                        progress_callback(len(image_files))

        logger.info(f"扫描完成，找到 {len(image_files)} 个图片文件")
        return image_files

    except Exception as e:
        logger.error(f"扫描目录失败: {e}")
        return []


def get_file_info(file_path: str) -> dict:
    """
    获取文件基本信息

    Args:
        file_path: 文件路径

    Returns:
        文件信息字典
    """
    stat = os.stat(file_path)
    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "modified_at": stat.st_mtime,
        "created_at": stat.st_ctime
    }
