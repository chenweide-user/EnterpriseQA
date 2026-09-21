"""
向量库服务

封装对 Chroma 的全部操作：
- 获取嵌入模型实例；
- 创建 / 删除 collection（与知识库一一对应）；
- 写入文档切片；
- 按文档删除切片；
- 带距离分数的相似度检索。
"""

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import settings

# 嵌入模型单例，避免重复初始化
_embeddings: OpenAIEmbeddings | None = None


def get_embeddings() -> OpenAIEmbeddings:
    """
    获取阿里云百炼文本嵌入模型实例（单例模式）。

    :return: OpenAIEmbeddings 实例
    """
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
            # 关闭 tiktoken 长度校验，避免非 OpenAI 模型名导致的问题
            check_embedding_ctx_length=False,
        )
    return _embeddings


def _get_client() -> chromadb.PersistentClient:
    """
    创建 Chroma 持久化客户端。

    :return: PersistentClient 实例
    """
    return chromadb.PersistentClient(path=settings.CHROMA_DIR)


def get_vectorstore(collection_name: str) -> Chroma:
    """
    获取 LangChain Chroma 向量存储对象（collection 不存在时会自动创建）。

    :param collection_name: 集合名称
    :return: Chroma 向量存储实例
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=settings.CHROMA_DIR,
    )


def create_collection(collection_name: str) -> None:
    """
    创建一个新的 Chroma collection。

    :param collection_name: 集合名称
    """
    _get_client().create_collection(name=collection_name)


def drop_collection(collection_name: str) -> None:
    """
    删除指定 Chroma collection（删除知识库时调用）。
    集合不存在时静默忽略。

    :param collection_name: 集合名称
    """
    client = _get_client()
    try:
        client.delete_collection(name=collection_name)
    except Exception:
        # Chroma 在集合不存在时会抛异常，这里统一忽略以保证幂等
        pass


def add_texts(
    collection_name: str, texts: list[str], metadatas: list[dict]
) -> None:
    """
    把一批文本切片及其元数据写入指定集合。

    :param collection_name: 集合名称
    :param texts: 文本切片列表
    :param metadatas: 与切片一一对应的元数据列表
    """
    vectorstore = get_vectorstore(collection_name)
    vectorstore.add_texts(texts=texts, metadatas=metadatas)


def delete_by_doc_id(collection_name: str, doc_id: int) -> None:
    """
    删除某个文档在向量库中的全部切片（删除文档时调用）。

    :param collection_name: 集合名称
    :param doc_id: 文档ID
    """
    client = _get_client()
    try:
        collection = client.get_collection(name=collection_name)
        # 入库时 doc_id 统一以字符串形式存储
        collection.delete(where={"doc_id": str(doc_id)})
    except Exception:
        pass


def search_with_scores(
    collection_name: str, question: str, top_k: int
) -> list[tuple]:
    """
    在指定集合中做相似度检索，返回文档切片及其距离分数。

    :param collection_name: 集合名称
    :param question: 用户问题
    :param top_k: 返回的切片数量
    :return: [(Document, score), ...]，分数越小越相似
    """
    vectorstore = get_vectorstore(collection_name)
    return vectorstore.similarity_search_with_score(question, k=top_k)
