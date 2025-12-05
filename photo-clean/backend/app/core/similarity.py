from typing import List, Dict, Set
from app.core.hash import compare_hashes
import logging

logger = logging.getLogger(__name__)


def find_similar_groups(
    image_hashes: Dict[str, str],
    threshold: int = 10
) -> List[List[str]]:
    """
    查找所有相似图片组

    Args:
        image_hashes: 图片路径到哈希值的映射
        threshold: 相似度阈值，汉明距离小于此值视为相似

    Returns:
        相似图片组列表，每组包含多个相似图片的路径
    """
    groups = []
    processed: Set[str] = set()

    image_paths = list(image_hashes.keys())

    for i, path1 in enumerate(image_paths):
        if path1 in processed:
            continue

        hash1 = image_hashes[path1]
        group = [path1]

        # 与后续所有图片比较
        for path2 in image_paths[i + 1:]:
            if path2 in processed:
                continue

            hash2 = image_hashes[path2]
            distance = compare_hashes(hash1, hash2)

            if distance < threshold:
                group.append(path2)
                processed.add(path2)

        # 只有找到相似图片才添加到组
        if len(group) > 1:
            groups.append(group)
            processed.add(path1)

    logger.info(f"找到 {len(groups)} 个相似图片组")
    return groups


def calculate_similarity_score(hash1: str, hash2: str) -> float:
    """
    计算相似度分数（百分比）

    Args:
        hash1: 第一个哈希值
        hash2: 第二个哈希值

    Returns:
        相似度分数 0-100，100表示完全相同
    """
    distance = compare_hashes(hash1, hash2)
    max_distance = 64  # 8x8 哈希最大汉明距离
    similarity = (1 - distance / max_distance) * 100
    return max(0, min(100, similarity))
