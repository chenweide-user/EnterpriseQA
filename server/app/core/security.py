"""
安全认证工具模块

提供：
1. 用户密码的 MD5 加密；
2. JWT 访问令牌的生成与解析。
"""

import hashlib
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def md5_encrypt(raw_password: str) -> str:
    """
    对明文密码进行 MD5 加密。

    :param raw_password: 明文密码
    :return: 32 位十六进制 MD5 字符串
    """
    return hashlib.md5(raw_password.encode("utf-8")).hexdigest()


def create_access_token(user_id: int, role: str) -> str:
    """
    根据用户信息生成 JWT 访问令牌。

    :param user_id: 用户ID
    :param role: 用户角色（admin/user）
    :return: 编码后的 JWT 字符串
    """
    # 令牌过期时间（使用带时区的 UTC 时间）
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # 载荷：sub 存用户ID，role 存角色，exp 存过期时间
    payload = {"sub": str(user_id), "role": role, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    解析并校验 JWT 令牌。

    :param token: JWT 字符串
    :return: 令牌载荷字典；令牌无效或过期时抛出 jwt 异常
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
