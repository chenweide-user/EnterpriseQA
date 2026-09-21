"""
通用依赖模块

提供 FastAPI 依赖函数：
1. get_current_user：从请求头的 JWT 中解析当前登录用户；
2. require_admin：在登录基础上进一步要求管理员角色。
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# Bearer Token 提取器：从 Authorization: Bearer <token> 请求头中取令牌
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    解析当前登录用户。

    :param credentials: 请求头中的 Bearer 令牌
    :param db: 数据库会话
    :return: 当前登录用户对象
    :raises HTTPException 401: 未携带令牌、令牌无效、用户不存在或被禁用
    """
    # 未携带令牌
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已失效",
        )

    # 解析令牌
    try:
        payload = decode_token(credentials.credentials)
        user_id = int(payload.get("sub"))
    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录令牌无效或已过期",
        )

    # 查询用户并校验状态
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    if user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="账号已被禁用"
        )
    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求当前用户必须是管理员。

    :param current_user: 当前登录用户
    :return: 当前管理员用户对象
    :raises HTTPException 403: 普通用户访问管理员接口
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，仅管理员可访问",
        )
    return current_user
