from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from app.config import settings

# 确保数据库目录存在
os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)

# 创建数据库引擎
SQLALCHEMY_DATABASE_URL = f"sqlite:///{settings.db_path}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ImageRecord(Base):
    """图片记录表"""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # 字节
    width = Column(Integer)
    height = Column(Integer)
    hash_value = Column(String, index=True)  # 感知哈希值
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime)
    scanned_at = Column(DateTime, default=datetime.utcnow)


class OperationLog(Base):
    """操作日志表"""
    __tablename__ = "operations"

    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String, nullable=False)  # delete, restore
    file_path = Column(String, nullable=False)
    trash_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_permanent = Column(Boolean, default=False)


class ScanTask(Base):
    """扫描任务表"""
    __tablename__ = "scan_tasks"

    id = Column(Integer, primary_key=True, index=True)
    scan_dir = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    similar_groups = Column(Integer, default=0)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


# 创建所有表
Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
