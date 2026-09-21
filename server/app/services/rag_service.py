"""
RAG 问答服务

实现完整的检索增强生成链路：
1. 多轮追问先结合历史对话改写为不依赖上下文的独立问题；
2. 在指定知识库的 Chroma collection 中检索相关切片；
3. 依据距离阈值判断是否命中；
4. 命中则拼装上下文与历史对话，调用 qwen3.7-flash 生成答案；
   未命中直接返回固定提示。
"""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.core.config import settings
from app.models.chat import ChatMessage
from app.services import vector_service

# 未命中知识库时的固定回复
NO_HIT_TEXT = "知识库没有相关信息。"

# 系统提示词：约束模型只能依据参考资料回答
SYSTEM_PROMPT = """你是企业内部知识库问答助手，请严格依据【参考资料】回答用户问题。
回答要求：
1. 只能使用参考资料中的信息，不得凭空编造；
2. 如果参考资料中没有与问题相关的内容，请直接回复"知识库没有相关信息"；
3. 使用中文回答，条理清晰、言简意赅。

【参考资料】
{context}"""

# 对话提示词模板：系统提示 + 历史消息占位 + 本轮问题
CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# 问题改写提示词：把多轮对话中的追问补全为独立问题（用于向量检索）
CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "根据对话历史，把用户的最新提问改写为一个不依赖上下文也能完整理解的中文问题。"
            "只输出改写后的问题本身，不要给出任何答案或解释。",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def get_llm() -> ChatOpenAI:
    """
    创建阿里云百炼对话大模型实例。

    :return: ChatOpenAI 实例（底层指向 qwen3.7-flash）
    """
    return ChatOpenAI(
        model=settings.CHAT_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_BASE_URL,
        temperature=0.1,
    )


def convert_history(messages: list[ChatMessage]) -> list[BaseMessage]:
    """
    把数据库中的历史消息转换为 LangChain 消息对象列表。

    :param messages: 历史对话消息（ChatMessage ORM 对象列表）
    :return: HumanMessage / AIMessage 列表
    """
    history: list[BaseMessage] = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        else:
            history.append(AIMessage(content=msg.content))
    return history


def condense_question(question: str, history_messages: list[BaseMessage]) -> str:
    """
    结合历史对话把追问改写为独立问题。

    例如历史中已问"远程办公每周可以申请几天？"，本轮追问"需要提前多久申请？"
    会被改写为"远程办公需要提前多久申请？"，从而保证向量检索的语义完整。

    :param question: 用户本轮问题
    :param history_messages: 历史对话消息列表
    :return: 改写后的独立问题
    """
    chain = CONDENSE_PROMPT | get_llm()
    response = chain.invoke(
        {
            "question": question,
            "history": history_messages,
        }
    )
    standalone = str(response.content).strip()
    # 极端情况下改写失败则回退使用原始问题
    return standalone or question


def generate_answer(
    collection_name: str,
    question: str,
    history_messages: list[BaseMessage] | None = None,
) -> str:
    """
    基于知识库生成问题答案（RAG 主流程）。

    :param collection_name: 知识库对应的 Chroma 集合名
    :param question: 用户本轮问题
    :param history_messages: 历史对话消息列表（用于多轮追问）
    :return: 模型生成的答案；未命中时返回固定提示语
    """
    history_messages = history_messages or []

    # 1. 存在历史对话时，先把追问改写为独立问题，再用于向量检索
    retrieval_query = (
        condense_question(question, history_messages)
        if history_messages
        else question
    )

    # 2. 向量检索
    results = vector_service.search_with_scores(
        collection_name, retrieval_query, settings.RETRIEVER_TOP_K
    )

    # 3. 距离阈值过滤：只保留命中的切片
    hit_docs = [
        (doc, float(score))
        for doc, score in results
        if float(score) <= settings.SCORE_THRESHOLD
    ]
    if not hit_docs:
        return NO_HIT_TEXT

    # 4. 拼装参考资料上下文
    context = "\n\n".join(
        f"[资料{index + 1}] {doc.page_content}"
        for index, (doc, _) in enumerate(hit_docs)
    )

    # 5. 调用大模型生成答案（LCEL 写法：提示词 | 模型）
    chain = CHAT_PROMPT | get_llm()
    response = chain.invoke(
        {
            "context": context,
            "question": question,
            "history": history_messages,
        }
    )
    return str(response.content)
