from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import (
    DeleteRequest, DeleteResponse,
    RestoreRequest, RestoreResponse
)
from app.services.image_service import ImageService
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/images", tags=["images"])


@router.get("/preview")
async def preview_image(file_path: str):
    """
    获取图片预览

    - **file_path**: 图片文件路径
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        if not os.path.isfile(file_path):
            raise HTTPException(status_code=400, detail="不是有效的文件")

        # 检查是否是支持的图片格式
        ext = os.path.splitext(file_path)[1].lower()
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')
        if ext not in supported_formats:
            raise HTTPException(status_code=400, detail="不支持的图片格式")

        return FileResponse(file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"预览图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览图片失败: {str(e)}")


@router.post("/delete", response_model=DeleteResponse)
async def delete_images(
    request: DeleteRequest,
    db: Session = Depends(get_db)
):
    """
    删除图片（移动到回收站）

    - **file_paths**: 要删除的文件路径列表
    """
    try:
        if not request.file_paths:
            raise HTTPException(status_code=400, detail="文件路径列表不能为空")

        service = ImageService(db)
        result = service.delete_images(request.file_paths)

        return DeleteResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除图片失败: {str(e)}")


@router.post("/restore", response_model=RestoreResponse)
async def restore_images(
    request: RestoreRequest,
    db: Session = Depends(get_db)
):
    """
    从回收站恢复图片

    - **file_paths**: 要恢复的原始文件路径列表
    """
    try:
        if not request.file_paths:
            raise HTTPException(status_code=400, detail="文件路径列表不能为空")

        service = ImageService(db)
        result = service.restore_images(request.file_paths)

        return RestoreResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢复图片失败: {e}")
        raise HTTPException(status_code=500, detail=f"恢复图片失败: {str(e)}")


@router.post("/clean-trash")
async def clean_trash(db: Session = Depends(get_db)):
    """
    清理回收站（删除超过保留期的文件）
    """
    try:
        service = ImageService(db)
        result = service.clean_trash()
        return result

    except Exception as e:
        logger.error(f"清理回收站失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理回收站失败: {str(e)}")


@router.get("/trash-info")
async def get_trash_info(db: Session = Depends(get_db)):
    """
    获取回收站信息
    """
    try:
        service = ImageService(db)
        result = service.get_trash_info()
        return result

    except Exception as e:
        logger.error(f"获取回收站信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取回收站信息失败: {str(e)}")
