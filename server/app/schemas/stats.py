"""
数据概览统计相关的 Pydantic 模型
"""

from pydantic import BaseModel, Field


class OverviewResponse(BaseModel):
    """数据概览响应模型：4 个核心指标 + 两个图表数据。"""

    user_count: int = Field(..., description="用户总数")
    kb_count: int = Field(..., description="知识库数量")
    doc_count: int = Field(..., description="文档总数")
    today_question_count: int = Field(..., description="今日提问数")
    # 近7天提问趋势：[{date: '2026-09-14', count: 3}, ...]
    week_trend: list[dict] = Field(default_factory=list, description="近7天提问趋势")
    # 知识库文档占比：[{name: '人事制度库', value: 2}, ...]
    kb_doc_ratio: list[dict] = Field(default_factory=list, description="知识库文档占比")
