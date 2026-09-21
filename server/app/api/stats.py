"""
数据概览统计路由模块（管理员）

提供首页所需的 4 个核心指标和两个图表数据：
- 用户总数、知识库数量、文档总数、今日提问数；
- 近 7 天提问趋势；
- 知识库文档占比。
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.db.session import get_db
from app.models.chat import ChatMessage
from app.models.document import Document
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.schemas.stats import OverviewResponse

# 统计路由
router = APIRouter(prefix="/api/stats", tags=["数据概览"])


@router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="数据概览（管理员）",
    dependencies=[Depends(require_admin)],
)
def overview(db: Session = Depends(get_db)):
    """
    汇总首页展示所需的全部统计数据。

    :param db: 数据库会话
    :return: 指标与图表数据
    """
    today = date.today()

    # ---- 4 个核心指标 ----
    user_count = db.scalar(select(func.count()).select_from(User))
    kb_count = db.scalar(select(func.count()).select_from(KnowledgeBase))
    doc_count = db.scalar(select(func.count()).select_from(Document))
    # 今日提问数：角色为 user 且消息日期为今天
    today_question_count = db.scalar(
        select(func.count())
        .select_from(ChatMessage)
        .where(
            ChatMessage.role == "user",
            func.date(ChatMessage.created_at) == today,
        )
    )

    # ---- 近 7 天提问趋势 ----
    # 一次性查询近7天有数据的日期及计数
    rows = db.execute(
        select(
            func.date(ChatMessage.created_at).label("day"),
            func.count().label("cnt"),
        )
        .where(
            ChatMessage.role == "user",
            ChatMessage.created_at >= today - timedelta(days=6),
        )
        .group_by("day")
    ).all()
    count_map = {str(day): cnt for day, cnt in rows}

    # 补齐没有提问的日期（计数为0），按时间正序排列
    week_trend = []
    for offset in range(6, -1, -1):
        day_str = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        week_trend.append({"date": day_str, "count": count_map.get(day_str, 0)})

    # ---- 知识库文档占比（左外连接，没有文档的知识库计数为0）----
    kb_rows = db.execute(
        select(KnowledgeBase.name, func.count(Document.id))
        .outerjoin(Document, Document.kb_id == KnowledgeBase.id)
        .group_by(KnowledgeBase.id, KnowledgeBase.name)
        .order_by(KnowledgeBase.id)
    ).all()
    kb_doc_ratio = [{"name": name, "value": cnt} for name, cnt in kb_rows]

    return OverviewResponse(
        user_count=user_count,
        kb_count=kb_count,
        doc_count=doc_count,
        today_question_count=today_question_count,
        week_trend=week_trend,
        kb_doc_ratio=kb_doc_ratio,
    )
