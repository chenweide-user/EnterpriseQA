"""
文档解析服务

将上传的 txt / md / pdf / docx 文档统一解析为纯文本，
供后续文本切片与向量化使用。
"""

from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def parse_document(file_path: str) -> str:
    """
    根据文件后缀选择对应的解析器，提取文档纯文本。

    :param file_path: 文档在服务器上的完整路径
    :return: 解析出的纯文本内容
    :raises ValueError: 文件类型不支持时抛出
    """
    ext = Path(file_path).suffix.lower()

    if ext in (".txt", ".md"):
        return _parse_text(file_path)
    if ext == ".pdf":
        return _parse_pdf(file_path)
    if ext == ".docx":
        return _parse_docx(file_path)

    raise ValueError(f"暂不支持的文件类型：{ext}")


def _parse_text(file_path: str) -> str:
    """
    解析纯文本文件（txt/md）。

    :param file_path: 文件路径
    :return: 文件文本内容
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _parse_pdf(file_path: str) -> str:
    """
    使用 pypdf 解析 PDF 文档，逐页提取文本。

    :param file_path: PDF 文件路径
    :return: 全部页面拼接后的文本
    """
    reader = PdfReader(file_path)
    page_texts = []
    for page in reader.pages:
        # extract_text 提取单页文本，空页返回空字符串
        text = page.extract_text() or ""
        page_texts.append(text)
    return "\n".join(page_texts)


def _parse_docx(file_path: str) -> str:
    """
    使用 python-docx 解析 Word 文档，提取所有段落文本。

    :param file_path: docx 文件路径
    :return: 全部段落拼接后的文本
    """
    doc = DocxDocument(file_path)
    paragraph_texts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraph_texts)
