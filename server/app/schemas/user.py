"""
用户相关的 Pydantic 模型

包含管理员创建/编辑用户、普通用户维护个人信息、修改密码等场景的结构。
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """用户公共字段基类。"""

    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")


class UserCreate(UserBase):
    """管理员创建用户请求模型。"""

    username: str = Field(..., min_length=2, max_length=50, description="登录用户名")
    password: str = Field(default="123456", min_length=6, max_length=50, description="初始密码")
    role: str = Field(default="user", description="角色：admin/user")
    status: int = Field(default=1, description="状态：1启用 0禁用")


class UserUpdate(BaseModel):
    """管理员编辑用户请求模型（不含密码，改密走单独接口）。"""

    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")
    role: Optional[str] = Field(default=None, description="角色：admin/user")
    status: Optional[int] = Field(default=None, description="状态：1启用 0禁用")


class UserProfileUpdate(BaseModel):
    """普通用户编辑个人信息请求模型（只能改自己的基础信息）。"""

    real_name: Optional[str] = Field(default=None, max_length=50, description="真实姓名")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    phone: Optional[str] = Field(default=None, max_length=20, description="手机号")


class PasswordUpdate(BaseModel):
    """修改密码请求模型。"""

    old_password: str = Field(..., min_length=1, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class UserResponse(UserBase):
    """用户信息响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="登录用户名")
    role: str = Field(..., description="角色")
    status: int = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
