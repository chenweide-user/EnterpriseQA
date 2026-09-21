"""
数据库会话模块

负责创建 SQLAlchemy 数据库引擎、会话工厂和声明式基类，
并提供 FastAPI 依赖函数 get_db。
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# 创建数据库引擎（此时并不真正建立连接，首次执行 SQL 时才连接）
# pool_pre_ping：取连接前先检测可用性，避免 MySQL 重启后拿到失效连接
# pool_recycle：连接最长存活 1 小时，防止 MySQL 主动断开空闲连接
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# 会话工厂
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 所有 ORM 模型的声明式基类
Base = declarative_base()


def get_db():
    """
    FastAPI 依赖函数：为每个请求提供一个独立的数据库会话，
    请求结束后自动关闭。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
