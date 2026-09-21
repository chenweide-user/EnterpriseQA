"""
智能问答路由模块

接收用户选择的知识库ID、问题和会话ID：
- 新会话（session_id 为空）自动创建会话；
- 已有会话携带最近 6 条历史消息支持多轮追问；
- 调用 RAG 服务生成答案，并把问答消息落库。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import rag_service

# 问答路由
router = APIRouter(prefix="/api/chat", tags=["智能问答"])


@router.post("", response_model=ChatResponse, summary="智能问答")
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    处理一次问答请求。

    :param payload: 知识库ID、问题、会话ID（可选）
    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 会话ID与AI回答
    :raises HTTPException 400/404: 会话归属错误 / 知识库不存在
    """
    # 校验知识库
    kb = db.get(KnowledgeBase, payload.kb_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="所选知识库不存在"
        )

    # 获取或新建会话
    session: ChatSession | None = None
    if payload.session_id is not None:
        session = db.get(ChatSession, payload.session_id)
        # 会话必须存在且属于当前用户
        if session is None or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="会话不存在或无权访问"
            )

    # 收集最近 6 条历史消息（按ID倒序取后再反转，保证时间顺序）
    history_langchain = []
    if session is not None:
        recent = db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.id.desc())
            .limit(6)
        ).all()
        history_langchain = rag_service.convert_history(list(reversed(recent)))
    else:
        # 新会话：标题取问题前 20 个字
        session = ChatSession(
            user_id=current_user.id,
            kb_id=kb.id,
            title=payload.question[:20],
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # 调用 RAG 服务生成答案
    answer = rag_service.generate_answer(
        kb.collection_name, payload.question, history_langchain
    )

    # 用户问题和AI回答分别落库
    db.add_all(
        [
            ChatMessage(session_id=session.id, role="user", content=payload.question),
            ChatMessage(session_id=session.id, role="assistant", content=answer),
        ]
    )
    db.commit()

    return ChatResponse(session_id=session.id, answer=answer)
