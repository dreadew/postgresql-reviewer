from typing import List, Dict, Any


class BaseVectorStore:
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        raise NotImplementedError
