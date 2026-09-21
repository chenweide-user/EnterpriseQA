"""
文档 ORM 模型

对应数据库表 document，记录上传文档的元数据与向量化处理状态。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Document(Base):
    """文档模型类：映射 document 表。"""

    __tablename__ = "document"

    # 文档ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="文档ID")
    # 所属知识库ID
    kb_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("knowledge_base.id"), nullable=False, comment="所属知识库ID"
    )
    # 原始文件名
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    # 服务器存储路径
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="文件存储路径")
    # 文件类型（后缀）
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件类型")
    # 文件大小（字节）
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, comment="文件大小(字节)")
    # 切片数量
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="切片数量")
    # 处理状态：processing / completed / failed
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="processing", comment="处理状态"
    )
    # 失败原因
    error_msg: Mapped[Optional[str]] = mapped_column(String(500), default=None, comment="错误信息")
    # 上传时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="上传时间"
    )

    # 关联：所属知识库
    knowledge_base: Mapped["KnowledgeBase"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        """对象的字符串表示。"""
        return f"<Document id={self.id} file_name={self.file_name!r} status={self.status!r}>"
