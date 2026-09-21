"""
知识库相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KBCreate(BaseModel):
    """创建知识库请求模型。"""

    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")


class KBUpdate(BaseModel):
    """编辑知识库请求模型（仅允许修改名称和描述）。"""

    name: Optional[str] = Field(default=None, min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")


class KBResponse(BaseModel):
    """知识库信息响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="知识库ID")
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    collection_name: str = Field(..., description="Chroma集合名")
    user_id: int = Field(..., description="创建人ID")
    doc_count: int = Field(..., description="文档数量")
    created_at: datetime = Field(..., description="创建时间")
