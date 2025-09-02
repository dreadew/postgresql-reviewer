import os
import glob
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.document import Document
from src.core.config import settings

from src.core.constants import FILE_ENCODING

import logging

logger = logging.getLogger(__name__)


def _read_rule_file(path: str) -> str:
    with open(path, "r", encoding=FILE_ENCODING) as f:
        return f.read()


def ingest_rules(rules_dir: str, rule_type: str = "sql"):
    """Загружает правила определенного типа в соответствующий FAISS индекс."""
    rules_dir = os.path.abspath(rules_dir)
    files = sorted(glob.glob(os.path.join(rules_dir, "**", "*.md"), recursive=True))
    if not files:
        logger.warning(f"Файлы с правилами не найдены в {rules_dir}")
        return

    embeddings = HuggingFaceEmbeddings(model_name=settings.embeddings_model)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )

    docs = []
    for p in files:
        text = _read_rule_file(p)
        title = Path(p).stem
        chunks = splitter.split_text(text)
        for ch in chunks:
            md = {"title": title, "source": p, "type": rule_type}
            docs.append({"page_content": ch, "metadata": md})

    lc_docs = [
        Document(page_content=d["page_content"], metadata=d["metadata"]) for d in docs
    ]
    store = FAISS.from_documents(lc_docs, embeddings)

    persist_dir = os.path.join(settings.faiss_persist_dir, rule_type)
    os.makedirs(persist_dir, exist_ok=True)
    store.save_local(persist_dir)
    logger.info(f"FAISS индекс для {rule_type} успешно сохранен в {persist_dir}")
