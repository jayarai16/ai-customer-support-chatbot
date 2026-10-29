"""
Document Retriever Module
Implements TF-IDF based retrieval for RAG (Retrieval-Augmented Generation).
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class TFIDFRetriever:
    """
    TF-IDF based document retriever for semantic search.
    Uses TF-IDF vectorization and cosine similarity to find relevant documents.
    """
    
    def __init__(self, documents: List[Dict[str, str]], max_features: int = 500):
        """
        Initialize the retriever with documents.
        
        Args:
            documents: List of documents with content to index
            max_features: Maximum number of TF-IDF features
        """
        self.documents = documents
        self.max_features = max_features
        self.vectorizer = None
        self.tfidf_matrix = None
        self._build_index()
    
    def _build_index(self) -> None:
        """Build TF-IDF index from documents"""
        if not self.documents:
            logger.warning("No documents provided for retriever")
            return
        
        # Extract content from documents
        contents = [doc.get("content", "") for doc in self.documents]
        
        try:
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=1,
                max_df=0.9
            )
            
            # Fit and transform documents
            self.tfidf_matrix = self.vectorizer.fit_transform(contents)
            logger.info(f"Built TF-IDF index with {len(self.documents)} documents")
        
        except Exception as e:
            logger.error(f"Error building TF-IDF index: {e}")
            raise
    
    def retrieve(self, query: str, top_k: int = 3, 
                threshold: float = 0.0) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve top-k most relevant documents for a query.
        
        Args:
            query: Search query
            top_k: Number of top documents to return
            threshold: Minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of (document, similarity_score) tuples
        """
        if not self.vectorizer or self.tfidf_matrix is None:
            logger.warning("Retriever not initialized with documents")
            return []
        
        try:
            # Vectorize the query
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarity scores
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Get top-k indices with threshold
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score >= threshold:
                    doc = self.documents[idx]
                    results.append((doc, score))
            
            logger.debug(f"Retrieved {len(results)} documents for query: {query}")
            return results
        
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
    
    def batch_retrieve(self, queries: List[str], top_k: int = 3,
                      threshold: float = 0.0) -> List[List[Tuple[Dict[str, Any], float]]]:
        """
        Retrieve documents for multiple queries.
        
        Args:
            queries: List of search queries
            top_k: Number of top documents per query
            threshold: Minimum similarity score
        
        Returns:
            List of result lists for each query
        """
        return [self.retrieve(query, top_k, threshold) for query in queries]
    
    def update_documents(self, documents: List[Dict[str, str]]) -> None:
        """
        Update the document collection and rebuild index.
        
        Args:
            documents: New list of documents
        """
        self.documents = documents
        self._build_index()
        logger.info(f"Updated retriever with {len(documents)} documents")


class HybridRetriever:
    """
    Hybrid retriever combining TF-IDF with additional ranking strategies.
    Improves relevance by considering document source type and other factors.
    """
    
    def __init__(self, documents: List[Dict[str, str]], max_features: int = 500):
        """
        Initialize hybrid retriever.
        
        Args:
            documents: List of documents with content to index
            max_features: Maximum number of TF-IDF features
        """
        self.tfidf_retriever = TFIDFRetriever(documents, max_features)
        self.source_weights = {
            "FAQ": 1.0,
            "Service": 0.9,
            "Pricing": 0.85,
            "Policy": 0.8
        }
    
    def retrieve(self, query: str, top_k: int = 3,
                threshold: float = 0.0) -> List[Tuple[Dict[str, Any], float]]:
        """
        Retrieve documents with hybrid scoring.
        Combines TF-IDF similarity with source-based weighting.
        
        Args:
            query: Search query
            top_k: Number of top documents to return
            threshold: Minimum similarity score
        
        Returns:
            List of (document, composite_score) tuples
        """
        # Get TF-IDF results
        tfidf_results = self.tfidf_retriever.retrieve(query, top_k * 2, threshold)
        
        # Apply source weighting
        weighted_results = []
        for doc, tfidf_score in tfidf_results:
            source = doc.get("source", "FAQ")
            weight = self.source_weights.get(source, 1.0)
            composite_score = tfidf_score * weight
            weighted_results.append((doc, composite_score))
        
        # Sort by composite score and return top-k
        weighted_results.sort(key=lambda x: x[1], reverse=True)
        return weighted_results[:top_k]
    
    def update_documents(self, documents: List[Dict[str, str]]) -> None:
        """Update documents in the underlying TF-IDF retriever"""
        self.tfidf_retriever.update_documents(documents)
