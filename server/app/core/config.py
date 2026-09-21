"""
全局配置模块

通过 pydantic-settings 统一读取 .env 文件和系统环境变量，
项目中所有其他模块都从这里获取配置，避免散落的硬编码。
"""

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 关闭 Chroma 匿名遥测上报（需在导入 chromadb 之前设置）
os.environ.setdefault("ANONYMIZED_TELEMETRY", "False")

# 后端根目录，即 server/ 目录
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """系统配置类：集中管理数据库、JWT、大模型、RAG 等全部配置项。"""

    # ---- MySQL 数据库配置 ----
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3308
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "db_enterprise_qa"

    # ---- JWT 登录令牌配置 ----
    JWT_SECRET_KEY: str = "enterprise-qa-secret-key-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # ---- 阿里云百炼模型配置 ----
    # API Key 从系统环境变量 DASHSCOPE_API_KEY 读取
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    CHAT_MODEL: str = "qwen3.7-flash"
    EMBEDDING_MODEL: str = "qwen3.7-text-embedding"

    # ---- 目录配置 ----
    CHROMA_DIR: str = str(BASE_DIR / "chroma_db")   # Chroma 持久化目录
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")     # 上传文件目录

    # ---- RAG 切片与检索参数 ----
    CHUNK_SIZE: int = 500           # 每个文本切片的最大字符数
    CHUNK_OVERLAP: int = 50         # 相邻切片之间的重叠字符数
    RETRIEVER_TOP_K: int = 4        # 每次检索返回的切片数量
    SCORE_THRESHOLD: float = 1.0    # 距离阈值，超过该值视为未命中知识库

    # 允许上传的文档后缀
    ALLOWED_EXTENSIONS: list[str] = [".txt", ".md", ".pdf", ".docx"]

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """拼接 SQLAlchemy 数据库连接串。"""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    # 指定 .env 文件位置；忽略多余的环境变量
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


# 全局唯一的配置实例
settings = Settings()

# 启动时自动确保运行目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
