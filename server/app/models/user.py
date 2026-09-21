"""
用户 ORM 模型

对应数据库表 sys_user，存储系统管理员和普通用户的账号信息。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    """用户模型类：映射 sys_user 表。"""

    __tablename__ = "sys_user"

    # 用户ID，主键自增
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    # 登录用户名，全局唯一
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="登录用户名")
    # 登录密码，MD5 加密后的 32 位字符串
    password: Mapped[str] = mapped_column(String(64), nullable=False, comment="登录密码（MD5）")
    # 真实姓名
    real_name: Mapped[Optional[str]] = mapped_column(String(50), default=None, comment="真实姓名")
    # 邮箱（全局唯一，允许为空）
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, default=None, comment="邮箱")
    # 手机号（全局唯一，允许为空）
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, default=None, comment="手机号")
    # 角色：admin 管理员 / user 普通用户
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", comment="角色：admin/user")
    # 状态：1 启用 / 0 禁用
    status: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, comment="状态：1启用 0禁用")
    # 创建时间（数据库端默认当前时间）
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    # 更新时间（更新记录时自动刷新）
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )

    # 关联：该用户创建的知识库列表
    knowledge_bases: Mapped[list["KnowledgeBase"]] = relationship(back_populates="creator")

    def __repr__(self) -> str:
        """对象的字符串表示，便于日志调试。"""
        return f"<User id={self.id} username={self.username!r} role={self.role!r}>"
