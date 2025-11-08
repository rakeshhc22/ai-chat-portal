"""
Embedding Service for AI Chat Portal
Handles semantic search and vector similarity
Uses Sentence Transformers for embeddings
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer, util
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning('sentence-transformers not installed. Semantic search disabled.')


class EmbeddingService:
    """
    Service for generating and managing embeddings
    Provides semantic search and similarity matching
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding service
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        self.model = None
        self.embeddings_cache = {}
        
        if TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                logger.info(f'Loaded embedding model: {model_name}')
            except Exception as e:
                logger.error(f'Failed to load embedding model: {str(e)}')
                TRANSFORMERS_AVAILABLE = False
    
    def is_available(self) -> bool:
        """Check if embedding service is available"""
        return self.model is not None
    
    def get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector or None if service unavailable
        """
        if not self.is_available():
            logger.warning('Embedding service not available')
            return None
        
        # Check cache first
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            # Cache the embedding
            self.embeddings_cache[text] = embedding
            return embedding
        except Exception as e:
            logger.error(f'Error generating embedding: {str(e)}')
            return None
    
    def get_embeddings_batch(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embeddings or None if service unavailable
        """
        if not self.is_available():
            logger.warning('Embedding service not available')
            return None
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            
            # Cache embeddings
            for text, embedding in zip(texts, embeddings):
                self.embeddings_cache[text] = embedding
            
            return embeddings
        except Exception as e:
            logger.error(f'Error generating batch embeddings: {str(e)}')
            return None
    
    def find_similar(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5,
        threshold: float = 0.3
    ) -> List[Tuple[str, float]]:
        """
        Find similar documents to query
        
        Args:
            query: Query text
            documents: List of documents to search
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of (document, similarity_score) tuples
        """
        if not self.is_available():
            logger.warning('Embedding service not available')
            return []
        
        try:
            # Get query embedding
            query_embedding = self.get_embedding(query)
            if query_embedding is None:
                return []
            
            # Get document embeddings
            doc_embeddings = self.get_embeddings_batch(documents)
            if doc_embeddings is None:
                return []
            
            # Calculate similarities
            similarities = util.cos_sim(query_embedding, doc_embeddings)[0]
            
            # Get top k results above threshold
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = [
                (documents[idx], float(similarities[idx]))
                for idx in top_indices
                if float(similarities[idx]) >= threshold
            ]
            
            return results
        except Exception as e:
            logger.error(f'Error finding similar documents: {str(e)}')
            return []
    
    def semantic_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Semantic search for documents
        
        Args:
            query: Query text
            documents: List of documents to search
            top_k: Number of top results to return
            
        Returns:
            List of search results with document and score
        """
        if not self.is_available():
            logger.warning('Embedding service not available')
            return []
        
        try:
            results = self.find_similar(query, documents, top_k)
            return [
                {
                    'document': doc,
                    'score': score,
                    'rank': idx + 1
                }
                for idx, (doc, score) in enumerate(results)
            ]
        except Exception as e:
            logger.error(f'Error in semantic search: {str(e)}')
            return []
    
    def get_similarity(self, text1: str, text2: str) -> Optional[float]:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1) or None if unavailable
        """
        if not self.is_available():
            logger.warning('Embedding service not available')
            return None
        
        try:
            embedding1 = self.get_embedding(text1)
            embedding2 = self.get_embedding(text2)
            
            if embedding1 is None or embedding2 is None:
                return None
            
            similarity = float(util.cos_sim(embedding1, embedding2)[0][0])
            return similarity
        except Exception as e:
            logger.error(f'Error calculating similarity: {str(e)}')
            return None
    
    def clear_cache(self):
        """Clear embedding cache"""
        self.embeddings_cache.clear()
        logger.info('Embedding cache cleared')


# Singleton instance for application-wide use
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
