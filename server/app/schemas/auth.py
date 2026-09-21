"""
认证相关的 Pydantic 模型

定义登录请求和登录成功后返回的令牌结构。
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求模型。"""

    # 用户名
    username: str = Field(..., min_length=1, max_length=50, description="登录用户名")
    # 密码（明文传输，由后端进行 MD5 比对）
    password: str = Field(..., min_length=1, max_length=50, description="登录密码")


class TokenResponse(BaseModel):
    """登录成功后的令牌响应模型。"""

    # JWT 访问令牌
    access_token: str = Field(..., description="JWT访问令牌")
    # 令牌类型，固定为 bearer
    token_type: str = Field(default="bearer", description="令牌类型")
