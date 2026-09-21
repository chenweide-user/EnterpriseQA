"""
文档管理路由模块

- 文档列表、上传、删除均为管理员功能；
- 上传文档时需指定所属知识库；
- 上传后同步执行：保存文件 -> 解析文本 -> 切片 -> 写入 Chroma。
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import BASE_DIR, settings
from app.core.deps import require_admin
from app.core.id_utils import next_available_id
from app.db.session import get_db
from app.models.document import Document
from app.models.knowledge import KnowledgeBase
from app.schemas.document import DocumentResponse
from app.services import vector_service
from app.services.document_parser import parse_document

# 文档路由
router = APIRouter(prefix="/api/documents", tags=["文档管理"])


@router.get(
    "",
    response_model=list[DocumentResponse],
    summary="文档列表（管理员）",
    dependencies=[Depends(require_admin)],
)
def list_documents(kb_id: int | None = None, db: Session = Depends(get_db)):
    """
    查询文档列表，可通过知识库ID过滤。

    :param kb_id: 知识库ID（可选）
    :param db: 数据库会话
    :return: 文档列表
    """
    stmt = select(Document).order_by(Document.id.desc())
    if kb_id is not None:
        stmt = stmt.where(Document.kb_id == kb_id)
    return db.scalars(stmt).all()


@router.post(
    "/upload",
    response_model=DocumentResponse,
    summary="上传文档（管理员）",
    dependencies=[Depends(require_admin)],
)
def upload_document(
    kb_id: int = Form(..., description="所属知识库ID"),
    file: UploadFile = File(..., description="文档文件"),
    db: Session = Depends(get_db),
):
    """
    上传文档并完成向量化入库。

    :param kb_id: 表单中的知识库ID
    :param file: 上传的文件对象
    :param db: 数据库会话
    :return: 处理完成的文档信息
    :raises HTTPException 400/404: 文件类型不支持 / 知识库不存在 / 解析失败
    """
    # 校验文件后缀
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅允许：{', '.join(settings.ALLOWED_EXTENSIONS)}",
        )

    # 校验知识库存在
    kb = db.get(KnowledgeBase, kb_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="所选知识库不存在"
        )

    # 读取文件内容并以 UUID 重命名保存，避免中文/重名问题
    file_bytes = file.file.read()
    saved_name = f"{uuid.uuid4().hex}{ext}"
    relative_path = os.path.join("uploads", saved_name)
    full_path = os.path.join(settings.UPLOAD_DIR, saved_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)

    # 创建文档记录，初始状态为 processing；ID 取最小可用值，删除后可自动填补空缺
    doc = Document(
        id=next_available_id(db, Document),
        kb_id=kb_id,
        file_name=file.filename,
        file_path=relative_path,
        file_type=ext.lstrip("."),
        file_size=len(file_bytes),
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 解析 -> 切片 -> 向量化
    try:
        # 1. 提取纯文本
        text = parse_document(full_path)
        # 2. 递归字符切片（按段落/换行/句号逐级切分）
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )
        chunks = splitter.split_text(text)
        # 3. 每个切片附带统一的元数据
        metadatas = [
            {
                "doc_id": str(doc.id),
                "kb_id": str(kb_id),
                "file_name": doc.file_name,
            }
            for _ in chunks
        ]
        # 4. 写入向量库
        if chunks:
            vector_service.add_texts(kb.collection_name, chunks, metadatas)

        # 更新文档状态
        doc.chunk_count = len(chunks)
        doc.status = "completed"
        kb.doc_count += 1
        db.commit()
        db.refresh(doc)
    except Exception as exc:
        # 解析或向量化失败：标记 failed 并返回错误
        doc.status = "failed"
        doc.error_msg = str(exc)[:500]
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文档处理失败：{exc}",
        )

    return doc


@router.delete(
    "/{doc_id}",
    summary="删除文档（管理员）",
    dependencies=[Depends(require_admin)],
)
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    删除文档：同步删除向量切片、物理文件和数据库记录。

    :param doc_id: 文档ID
    :param db: 数据库会话
    :return: 操作结果提示
    :raises HTTPException 404: 文档不存在
    """
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在"
        )

    kb = db.get(KnowledgeBase, doc.kb_id)
    # 删除向量库中的该文档切片
    if kb is not None:
        vector_service.delete_by_doc_id(kb.collection_name, doc.id)

    # 删除服务器上的物理文件
    try:
        physical_file = BASE_DIR / doc.file_path
        if physical_file.exists():
            physical_file.unlink()
    except Exception:
        pass

    # 已完成入库的文档才扣减知识库文档计数
    if kb is not None and doc.status == "completed" and kb.doc_count > 0:
        kb.doc_count -= 1

    db.delete(doc)
    db.commit()
    return {"message": "删除成功"}
