"""
对话历史路由模块

用户只能查看和删除属于自己的问答会话。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatSession
from app.models.user import User
from app.schemas.chat import SessionDetailResponse, SessionResponse

# 对话历史路由
router = APIRouter(prefix="/api/history", tags=["对话历史"])


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    summary="我的会话列表",
)
def list_sessions(
    kb_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询当前用户的全部问答会话，可按知识库过滤。

    :param kb_id: 知识库ID（可选）
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 会话列表
    """
    stmt = (
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.id.desc())
    )
    if kb_id is not None:
        stmt = stmt.where(ChatSession.kb_id == kb_id)
    return db.scalars(stmt).all()


@router.get(
    "/sessions/{session_id}",
    response_model=SessionDetailResponse,
    summary="会话详情（含全部消息）",
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取指定会话的详情及其全部消息。

    :param session_id: 会话ID
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 会话详情
    :raises HTTPException 404: 会话不存在或不属于当前用户
    """
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权查看",
        )
    return session


@router.delete("/sessions/{session_id}", summary="删除会话")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    删除指定会话（消息随会话级联删除）。

    :param session_id: 会话ID
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 操作结果提示
    :raises HTTPException 404: 会话不存在或不属于当前用户
    """
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在或无权删除",
        )

    db.delete(session)
    db.commit()
    return {"message": "删除成功"}
