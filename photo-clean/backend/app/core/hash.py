import imagehash
from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_image_hash(image_path: str, hash_size: int = 8) -> Optional[str]:
    """
    计算图片的感知哈希值

    Args:
        image_path: 图片文件路径
        hash_size: 哈希大小，默认8（生成64位哈希）

    Returns:
        哈希值字符串，失败返回None
    """
    try:
        with Image.open(image_path) as img:
            # 使用感知哈希算法
            phash = imagehash.phash(img, hash_size=hash_size)
            return str(phash)
    except Exception as e:
        logger.error(f"计算图片哈希失败: {image_path}, 错误: {e}")
        return None


def get_image_info(image_path: str) -> Optional[dict]:
    """
    获取图片基本信息

    Args:
        image_path: 图片文件路径

    Returns:
        包含宽度、高度等信息的字典
    """
    try:
        with Image.open(image_path) as img:
            return {
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "format": img.format
            }
    except Exception as e:
        logger.error(f"读取图片信息失败: {image_path}, 错误: {e}")
        return None


def compare_hashes(hash1: str, hash2: str) -> int:
    """
    计算两个哈希值的汉明距离

    Args:
        hash1: 第一个哈希值
        hash2: 第二个哈希值

    Returns:
        汉明距离（0-64），值越小越相似
    """
    try:
        h1 = imagehash.hex_to_hash(hash1)
        h2 = imagehash.hex_to_hash(hash2)
        return h1 - h2
    except Exception as e:
        logger.error(f"比较哈希失败: {e}")
        return 999  # 返回一个很大的值表示完全不相似
