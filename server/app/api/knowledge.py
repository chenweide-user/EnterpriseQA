"""
知识库管理路由模块

- 查询：登录用户均可访问（智能问答页面需要加载知识库下拉列表）；
- 新增 / 修改 / 删除：仅管理员；
- 创建知识库时同步在 Chroma 中创建 collection，删除时同步删除。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.core.id_utils import next_available_id
from app.db.session import get_db
from app.models.knowledge import KnowledgeBase
from app.models.user import User
from app.schemas.knowledge import KBCreate, KBResponse, KBUpdate
from app.services import vector_service

# 知识库路由
router = APIRouter(prefix="/api/knowledge", tags=["知识库管理"])


@router.get("", response_model=list[KBResponse], summary="知识库列表")
def list_knowledge(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    查询全部知识库列表。

    :param db: 数据库会话
    :param current_user: 当前登录用户
    :return: 知识库列表
    """
    return db.scalars(select(KnowledgeBase).order_by(KnowledgeBase.id)).all()


@router.post(
    "",
    response_model=KBResponse,
    status_code=status.HTTP_201_CREATED,
    summary="新建知识库（管理员）",
    dependencies=[Depends(require_admin)],
)
def create_knowledge(
    payload: KBCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    新建知识库，同时创建对应的 Chroma collection。

    :param payload: 知识库名称与描述
    :param db: 数据库会话
    :param current_user: 当前登录的管理员
    :return: 新建的知识库信息
    :raises HTTPException 400: 知识库名称已存在
    """
    # 名称唯一性校验
    exists = db.scalar(select(KnowledgeBase).where(KnowledgeBase.name == payload.name))
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="知识库名称已存在"
        )

    # 生成唯一的 Chroma collection 名称（kb_ + 12位UUID）
    collection_name = f"kb_{uuid.uuid4().hex[:12]}"
    vector_service.create_collection(collection_name)

    # 写入知识库记录；ID 取最小可用值，删除后可自动填补空缺
    kb = KnowledgeBase(
        id=next_available_id(db, KnowledgeBase),
        name=payload.name,
        description=payload.description,
        collection_name=collection_name,
        user_id=current_user.id,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@router.put(
    "/{kb_id}",
    response_model=KBResponse,
    summary="编辑知识库（管理员）",
    dependencies=[Depends(require_admin)],
)
def update_knowledge(
    kb_id: int, payload: KBUpdate, db: Session = Depends(get_db)
):
    """
    修改知识库名称或描述（不影响向量数据）。

    :param kb_id: 知识库ID
    :param payload: 待更新字段
    :param db: 数据库会话
    :return: 更新后的知识库信息
    :raises HTTPException 400/404: 名称重复 / 知识库不存在
    """
    kb = db.get(KnowledgeBase, kb_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )

    # 若修改名称，需校验新名称唯一
    if payload.name is not None and payload.name != kb.name:
        exists = db.scalar(
            select(KnowledgeBase).where(KnowledgeBase.name == payload.name)
        )
        if exists is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="知识库名称已存在"
            )
        kb.name = payload.name

    if payload.description is not None:
        kb.description = payload.description

    db.commit()
    db.refresh(kb)
    return kb


@router.delete(
    "/{kb_id}",
    summary="删除知识库（管理员）",
    dependencies=[Depends(require_admin)],
)
def delete_knowledge(kb_id: int, db: Session = Depends(get_db)):
    """
    删除知识库：级联删除文档记录，并删除对应的 Chroma collection。

    :param kb_id: 知识库ID
    :param db: 数据库会话
    :return: 操作结果提示
    :raises HTTPException 404: 知识库不存在
    """
    kb = db.get(KnowledgeBase, kb_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
        )

    # 先删除向量集合，再删除数据库记录（文档通过外键级联删除）
    vector_service.drop_collection(kb.collection_name)
    db.delete(kb)
    db.commit()
    return {"message": "删除成功"}
