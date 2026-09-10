"""
文档加载与切片模块
支持: Markdown / PDF / Word
使用LangChain文档加载器，统一返回Document对象
"""
import os
import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

logger = logging.getLogger('ai_service')

# 中文优先的递归分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n\n", "\n", "。", "；", "，", " ", ""],
)

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ],
)


def load_and_split(file_path: str, project_id: int, module_id: int = None) -> List[Document]:
    """
    加载文档并切片
    支持: .md, .pdf, .docx
    返回Document列表，metadata包含project_id, module_id, source
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.md':
        docs = _load_markdown(file_path)
    elif ext == '.pdf':
        docs = _load_pdf(file_path)
    elif ext == '.docx':
        docs = _load_docx(file_path)
    else:
        # 纯文本兜底
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        docs = [Document(page_content=content, metadata={"source": file_path})]

    # 切片
    chunks = _split_documents(docs)

    # 补充元数据
    for chunk in chunks:
        chunk.metadata['project_id'] = project_id
        chunk.metadata['module_id'] = module_id or 0
        chunk.metadata['doc_type'] = ext.lstrip('.')

    logger.info(f"文档 {file_path} 加载完成，共 {len(chunks)} 个切片")
    return chunks


def _load_markdown(file_path: str) -> List[Document]:
    """加载Markdown文档，按标题切分"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        md_docs = markdown_splitter.split_text(content)
        if md_docs:
            return md_docs
    except Exception as e:
        logger.warning(f"Markdown标题切分失败，降级为纯文本: {e}")

    return [Document(page_content=content, metadata={"source": file_path})]


def _load_pdf(file_path: str) -> List[Document]:
    """加载PDF文档"""
    from langchain_community.document_loaders import PyMuPDFLoader
    loader = PyMuPDFLoader(file_path)
    return loader.load()


def _load_docx(file_path: str) -> List[Document]:
    """加载Word文档"""
    from langchain_community.document_loaders import Docx2txtLoader
    loader = Docx2txtLoader(file_path)
    return loader.load()


def _split_documents(docs: List[Document]) -> List[Document]:
    """递归切片"""
    all_chunks = []
    for doc in docs:
        chunks = text_splitter.split_documents([doc])
        all_chunks.extend(chunks)
    return all_chunks
