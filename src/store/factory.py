import os
from src.store.faiss import FaissVectorStore
from src.core.config import settings


class VectorStoreFactory:
    @staticmethod
    def create(store_type: str = "sql"):
        if settings.vector_store == "faiss":
            persist_dir = os.path.join(settings.faiss_persist_dir, store_type)
            return FaissVectorStore(persist_dir=persist_dir)
        raise ValueError(f"Unknown vector store: {settings.vector_store}")
