"""RAG Manager - Orchestrates data collection, normalization, and embedding"""

import logging
from typing import Optional

from services.kamco_collector_service import KamcoCollectorService
from normalize.kamco_normalizer import normalize
from rag.embed import embed, setup_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGManager:
    """Manages the complete RAG pipeline for KAMCO data"""
    
    def __init__(self, service_key: Optional[str] = None):
        self.service_key = service_key
        self.collector = None
        
    def collect_and_process(
        self,
        max_pages: int = 5,
        auto_normalize: bool = True,
        auto_embed: bool = True,
        recreate_collection: bool = False
    ) -> dict:
        """
        Collect data from KAMCO API and process it through the RAG pipeline
        
        Args:
            max_pages: Maximum number of pages to collect
            auto_normalize: Automatically normalize data after collection
            auto_embed: Automatically embed data after normalization
            recreate_collection: Recreate Qdrant collection (warning: deletes existing data)
            
        Returns:
            dict: Statistics about the operation
        """
        stats = {
            "collection": {},
            "normalization": False,
            "embedding": False,
            "errors": []
        }
        
        # Step 1: Collect data
        try:
            logger.info(f"Starting data collection (max {max_pages} pages)...")
            self.collector = KamcoCollectorService(service_key=self.service_key)
            
            if not self.collector.connect_mongodb():
                stats["errors"].append("Failed to connect to MongoDB")
                return stats
            
            collection_result = self.collector.collect_data(max_pages=max_pages)
            stats["collection"] = collection_result
            logger.info(f"Collection completed: {collection_result}")
            
            self.collector.close_mongodb()
            
        except Exception as e:
            error_msg = f"Data collection error: {str(e)}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
        
        # Step 2: Normalize data
        if auto_normalize:
            try:
                logger.info("Starting data normalization...")
                normalize()
                stats["normalization"] = True
                logger.info("Normalization completed")
            except Exception as e:
                error_msg = f"Normalization error: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
                return stats
        
        # Step 3: Embed data
        if auto_embed:
            try:
                logger.info("Starting data embedding...")
                
                # Optionally recreate collection
                if recreate_collection:
                    logger.warning("Recreating Qdrant collection (existing data will be deleted)")
                    setup_collection()
                
                embed()
                stats["embedding"] = True
                logger.info("Embedding completed")
            except Exception as e:
                error_msg = f"Embedding error: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
                return stats
        
        return stats
    
    def normalize_only(self) -> bool:
        """Normalize existing collected data"""
        try:
            logger.info("Normalizing existing data...")
            normalize()
            logger.info("Normalization completed")
            return True
        except Exception as e:
            logger.error(f"Normalization error: {e}")
            return False
    
    def embed_only(self, recreate_collection: bool = False) -> bool:
        """Embed existing normalized data"""
        try:
            logger.info("Embedding existing data...")
            
            if recreate_collection:
                logger.warning("Recreating Qdrant collection")
                setup_collection()
            
            embed()
            logger.info("Embedding completed")
            return True
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    manager = RAGManager()
    
    # Collect, normalize, and embed in one go
    result = manager.collect_and_process(
        max_pages=3,
        auto_normalize=True,
        auto_embed=True,
        recreate_collection=False
    )
    
    print("\nRAG Pipeline Results:")
    print(f"Collection: {result['collection']}")
    print(f"Normalization: {'✓' if result['normalization'] else '✗'}")
    print(f"Embedding: {'✓' if result['embedding'] else '✗'}")
    
    if result['errors']:
        print(f"\nErrors: {result['errors']}")
