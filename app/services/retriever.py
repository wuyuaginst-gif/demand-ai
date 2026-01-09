import logging
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DemandRetriever:
    """相似需求检索服务"""

    def __init__(self, base_url: str, model: str, persist_dir: str, collection_name: str = "demands"):
        self.embeddings = OllamaEmbeddings(
            base_url=base_url,
            model=model
        )
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_dir
        )
        logger.info(f"ChromaDB 初始化完成: {persist_dir}")

    def add_demand(self, demand_id: str, content: str, metadata: dict = None) -> bool:
        """存储需求"""
        try:
            doc = Document(
                page_content=content,
                metadata={"demand_id": demand_id, **(metadata or {})}
            )
            self.vectorstore.add_documents([doc], ids=[demand_id])
            logger.info(f"需求已存储: {demand_id}")
            return True
        except Exception as e:
            logger.error(f"存储失败: {e}")
            raise

    def find_similar(self, query: str, k: int = 3) -> list:
        """查找相似需求"""
        try:
            collection = self.vectorstore._collection
            if collection.count() == 0:
                return []
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            return [
                {
                    "demand_id": doc.metadata.get("demand_id"),
                    "content": doc.page_content[:200] + ("..." if len(doc.page_content) > 200 else ""),
                    "score": round(float(score), 4)
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"检索失败: {e}")
            raise

    def get_stats(self) -> dict:
        """获取统计信息"""
        try:
            collection = self.vectorstore._collection
            return {"total_documents": collection.count(), "collection_name": collection.name}
        except Exception as e:
            return {"error": str(e)}
