"""
问答会话与消息 ORM 模型

对应数据库表 chat_session 和 chat_message，
记录用户的每一次问答会话及会话内的逐条消息。
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ChatSession(Base):
    """问答会话模型类：映射 chat_session 表。"""

    __tablename__ = "chat_session"

    # 会话ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="会话ID")
    # 提问用户ID
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="提问用户ID")
    # 选择的知识库ID
    kb_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="知识库ID")
    # 会话标题
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="会话标题")
    # 创建时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    # 关联：会话下的全部消息；删除会话时级联删除消息
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )

    def __repr__(self) -> str:
        """对象的字符串表示。"""
        return f"<ChatSession id={self.id} title={self.title!r}>"


class ChatMessage(Base):
    """对话消息模型类：映射 chat_message 表。"""

    __tablename__ = "chat_message"

    # 消息ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="消息ID")
    # 所属会话ID
    session_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chat_session.id"), nullable=False, comment="所属会话ID"
    )
    # 角色：user 用户提问 / assistant AI 回答
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色：user/assistant")
    # 消息内容
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    # 消息时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="消息时间"
    )

    # 关联：所属会话
    session: Mapped["ChatSession"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        """对象的字符串表示。"""
        return f"<ChatMessage id={self.id} role={self.role!r}>"
