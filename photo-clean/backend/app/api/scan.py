from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import (
    ScanRequest, ScanResponse, ScanProgress
)
from app.services.scan_service import ScanService
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])


def run_scan_task(task_id: int, scan_dir: str, recursive: bool, threshold: int, db: Session):
    """后台运行扫描任务"""
    try:
        service = ScanService(db)
        service.scan_and_process(
            task_id=task_id,
            scan_dir=scan_dir,
            recursive=recursive,
            threshold=threshold,
            workers=settings.scan_workers
        )
    except Exception as e:
        logger.error(f"扫描任务执行失败: {e}")
    finally:
        db.close()


@router.post("/start", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    开始扫描任务

    - **scan_dir**: 要扫描的目录路径（可选，默认使用配置的照片目录）
    - **recursive**: 是否递归扫描子目录
    - **threshold**: 相似度阈值（默认10）
    """
    try:
        # 如果未指定扫描目录，使用配置的默认目录
        import os
        scan_dir = request.scan_dir if request.scan_dir else settings.photo_dir

        # 验证目录是否存在
        if not os.path.exists(scan_dir):
            raise HTTPException(status_code=400, detail=f"扫描目录不存在: {scan_dir}")

        if not os.path.isdir(scan_dir):
            raise HTTPException(status_code=400, detail="路径不是目录")

        # 创建扫描任务
        service = ScanService(db)
        task = service.create_scan_task(scan_dir)

        # 在后台运行扫描
        background_tasks.add_task(
            run_scan_task,
            task.id,
            scan_dir,
            request.recursive,
            request.threshold,
            db
        )

        return ScanResponse(
            task_id=task.id,
            status="running",
            message="扫描任务已启动"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动扫描失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动扫描失败: {str(e)}")


@router.get("/progress/{task_id}", response_model=ScanProgress)
async def get_scan_progress(task_id: int, db: Session = Depends(get_db)):
    """
    获取扫描任务进度

    - **task_id**: 任务ID
    """
    try:
        service = ScanService(db)
        progress = service.get_task_progress(task_id)

        if not progress:
            raise HTTPException(status_code=404, detail="任务不存在")

        return ScanProgress(**progress)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取进度失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.get("/groups/{task_id}")
async def get_similar_groups(
    task_id: int,
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取相似图片组（分页）

    - **task_id**: 任务ID
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（默认100）
    """
    try:
        if page < 1:
            raise HTTPException(status_code=400, detail="页码必须大于0")

        if page_size < 1 or page_size > 500:
            raise HTTPException(status_code=400, detail="每页数量必须在1-500之间")

        service = ScanService(db)
        groups = service.get_similar_groups(task_id)

        # 计算分页
        total_groups = len(groups)
        total_pages = (total_groups + page_size - 1) // page_size

        # 获取当前页数据
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_groups = groups[start_idx:end_idx]

        return {
            "task_id": task_id,
            "total_groups": total_groups,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "groups": page_groups
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取相似图片组失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取相似图片组失败: {str(e)}")
