"""
认证路由模块

提供用户登录（校验 MD5 密码并签发 JWT）和获取当前登录用户信息接口。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, md5_encrypt
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse

# 认证路由，统一前缀 /api/auth
router = APIRouter(prefix="/api/auth", tags=["认证管理"])


@router.post("/login", response_model=TokenResponse, summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口。

    :param payload: 用户名与明文密码
    :param db: 数据库会话
    :return: JWT 访问令牌
    :raises HTTPException 400: 用户名或密码错误、账号被禁用
    """
    # 按用户名查询用户
    user = db.scalar(select(User).where(User.username == payload.username))

    # 用户不存在或密码 MD5 比对失败
    if user is None or user.password != md5_encrypt(payload.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或密码错误",
        )

    # 账号被禁用
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="账号已被禁用，请联系管理员",
        )

    # 签发令牌并返回
    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse, summary="获取当前登录用户信息")
def get_me(current_user: User = Depends(get_current_user)):
    """
    获取当前登录用户的详细信息。

    :param current_user: 由依赖注入的当前登录用户
    :return: 用户信息
    """
    return current_user
