"""
知识库 ORM 模型

对应数据库表 knowledge_base，记录知识库的基本信息，
每个知识库对应 Chroma 中的一个 collection。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class KnowledgeBase(Base):
    """知识库模型类：映射 knowledge_base 表。"""

    __tablename__ = "knowledge_base"

    # 知识库ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="知识库ID")
    # 知识库名称，唯一
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="知识库名称")
    # 知识库描述
    description: Mapped[Optional[str]] = mapped_column(Text, default=None, comment="知识库描述")
    # 对应的 Chroma collection 名称
    collection_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="Chroma集合名")
    # 创建人ID
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sys_user.id"), nullable=False, comment="创建人ID"
    )
    # 文档数量（冗余计数，便于列表展示）
    doc_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="文档数量")
    # 创建时间 / 更新时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关联：知识库创建人
    creator: Mapped["User"] = relationship(back_populates="knowledge_bases")
    # 关联：知识库下的全部文档；删除知识库时级联删除文档记录
    documents: Mapped[list["Document"]] = relationship(
        back_populates="knowledge_base", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """对象的字符串表示。"""
        return f"<KnowledgeBase id={self.id} name={self.name!r}>"
