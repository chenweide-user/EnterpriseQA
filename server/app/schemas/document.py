"""
文档相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DocumentResponse(BaseModel):
    """文档信息响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="文档ID")
    kb_id: int = Field(..., description="所属知识库ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小(字节)")
    chunk_count: int = Field(..., description="切片数量")
    status: str = Field(..., description="处理状态")
    error_msg: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(..., description="上传时间")
