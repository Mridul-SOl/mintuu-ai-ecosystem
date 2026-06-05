import os
import logging
from typing import Dict, Any, List, Optional
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

logger = logging.getLogger("mintuu.memory.vector")

class VectorMemory:
    """Semantic vector memory using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./database/chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        
        if chromadb is None:
            logger.warning("ChromaDB not installed. Vector memory disabled.")
            return
            
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Create collections for different memory tiers
            self.collections = {
                "workflows": self.client.get_or_create_collection("workflows"),
                "decisions": self.client.get_or_create_collection("decisions"),
                "org_knowledge": self.client.get_or_create_collection("org_knowledge"),
                "agent_memory": self.client.get_or_create_collection("agent_memory")
            }
            logger.info(f"Vector memory initialized at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            
    def store_memory(self, collection_name: str, document: str, metadata: Dict[str, Any], memory_id: str):
        """Store a new memory embedding."""
        if not self.client or collection_name not in self.collections:
            return
            
        try:
            collection = self.collections[collection_name]
            collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[memory_id]
            )
            logger.debug(f"Stored memory {memory_id} in {collection_name}")
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            
    def search_memory(self, collection_name: str, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for semantically similar memories."""
        if not self.client or collection_name not in self.collections:
            return []
            
        try:
            collection = self.collections[collection_name]
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            formatted_results = []
            if results and results.get("documents") and len(results["documents"]) > 0:
                for i in range(len(results["documents"][0])):
                    formatted_results.append({
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "distance": results["distances"][0][i] if results.get("distances") else 0.0
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []
