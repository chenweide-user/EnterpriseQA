"""
智能问答与对话历史相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """智能问答请求模型。"""

    kb_id: int = Field(..., description="选择的知识库ID")
    question: str = Field(..., min_length=1, description="用户问题")
    # 会话ID为空时表示开启一个新会话
    session_id: Optional[int] = Field(default=None, description="会话ID，为空则新建会话")


class ChatResponse(BaseModel):
    """智能问答响应模型。"""

    session_id: int = Field(..., description="本次问答所属会话ID")
    answer: str = Field(..., description="AI回答内容")


class MessageResponse(BaseModel):
    """单条对话消息响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="消息ID")
    role: str = Field(..., description="角色：user/assistant")
    content: str = Field(..., description="消息内容")
    created_at: datetime = Field(..., description="消息时间")


class SessionResponse(BaseModel):
    """会话列表项响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="会话ID")
    kb_id: int = Field(..., description="知识库ID")
    title: str = Field(..., description="会话标题")
    created_at: datetime = Field(..., description="创建时间")


class SessionDetailResponse(SessionResponse):
    """会话详情响应模型：在会话信息基础上附带全部消息。"""

    messages: list[MessageResponse] = Field(default_factory=list, description="会话消息列表")
