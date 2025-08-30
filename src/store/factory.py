import os
from src.store.faiss import FaissVectorStore
from src.core.config import settings


class VectorStoreFactory:
    @staticmethod
    def create(store_type: str = "sql"):
        if settings.vector_store == "faiss":
            if store_type == "sql":
                persist_dir = os.path.join(settings.faiss_persist_dir, "sql")
            elif store_type == "config":
                persist_dir = os.path.join(settings.faiss_persist_dir, "config")
            else:
                persist_dir = settings.faiss_persist_dir
            return FaissVectorStore(persist_dir=persist_dir)
        raise ValueError(f"Unknown vector store: {settings.vector_store}")
