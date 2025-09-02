import os
from src.store.base import BaseVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from src.core.config import settings

import logging

logger = logging.getLogger(__name__)


class FaissVectorStore(BaseVectorStore):
    def __init__(self, persist_dir: str = settings.faiss_persist_dir):
        self.persist_dir = persist_dir
        self.emb = HuggingFaceEmbeddings(model_name=settings.embeddings_model)

        index_path = os.path.join(self.persist_dir, "index.faiss")
        if os.path.exists(index_path):
            logger.info(f"Loading FAISS index from {self.persist_dir}")
            self.store = FAISS.load_local(
                self.persist_dir, self.emb, allow_dangerous_deserialization=True
            )
            logger.info(
                f"FAISS index loaded successfully with {self.store.index.ntotal} vectors"
            )
        else:
            logger.warning(
                f"FAISS index not found at {index_path}, creating empty store"
            )
            self.store = FAISS.from_texts(["dummy"], self.emb)
            self.store.delete([self.store.index_to_docstore_id[0]])

    def save_index(self):
        os.makedirs(self.persist_dir, exist_ok=True)
        self.store.save_local(self.persist_dir)

    def similarity_search(self, query, k=5):
        logger.info(f"Performing similarity search for query: '{query}' with k={k}")
        hits = self.store.similarity_search_with_score(query, k)
        logger.info(f"Found {len(hits)} similar documents")
        out = []
        for doc, score in hits:
            out.append(
                {
                    "title": doc.metadata.get("title", ""),
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                }
            )
        return out
