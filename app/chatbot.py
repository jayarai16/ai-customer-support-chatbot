"""
Chatbot Module
Core chatbot implementation with Groq LLM and RAG (Retrieval-Augmented Generation).
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from groq import Groq
from app.knowledge_base import KnowledgeBase
from app.retriever import HybridRetriever
from app.config import config

logger = logging.getLogger(__name__)


class GroqChatbot:
    """
    AI-powered chatbot using Groq API with RAG architecture.
    Answers customer support questions based on business knowledge base.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase):
        """
        Initialize the chatbot.
        
        Args:
            knowledge_base: KnowledgeBase instance with business information
        """
        self.kb = knowledge_base
        self.retriever = HybridRetriever(
            documents=knowledge_base.get_documents(),
            max_features=config.TFIDF_MAX_FEATURES
        )
        
        # Initialize Groq client
        self.client = Groq(api_key=config.GROQ_API_KEY)
        
        # Conversation history for context
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info("Chatbot initialized with Groq API")
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the chatbot"""
        business_info = self.kb.get_business_info()
        company_name = business_info.get("name", "our company")
        
        return f"""You are a professional and helpful customer support assistant for {company_name}.

Your responsibilities:
1. Answer customer questions accurately based on the provided knowledge base
2. Be friendly, professional, and helpful in all interactions
3. If information is not available in the knowledge base, clearly state that
4. Never make up or assume information - if you don't know, say so
5. Suggest relevant alternatives or next steps when appropriate
6. Offer to escalate to human support for complex issues if needed

Guidelines:
- Keep responses concise but informative
- Use clear language and avoid jargon
- Be empathetic to customer concerns
- Provide specific details when available
- If a question is outside your scope, politely decline and offer alternatives

Important: Only use information from the provided context. Do not hallucinate or invent details about products, pricing, or policies that aren't in the knowledge base."""
    
    def retrieve_context(self, query: str, top_k: int = 3) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Retrieve relevant documents from knowledge base.
        
        Args:
            query: User's question
            top_k: Number of top documents to retrieve
        
        Returns:
            Tuple of (documents, similarity_scores)
        """
        results = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            threshold=config.SIMILARITY_THRESHOLD
        )
        
        if not results:
            logger.debug(f"No relevant documents found for query: {query}")
            return [], []
        
        documents = [doc for doc, _ in results]
        scores = [score for _, score in results]
        
        logger.debug(f"Retrieved {len(documents)} relevant documents for query")
        return documents, scores
    
    def _format_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for the LLM.
        
        Args:
            documents: Retrieved documents
        
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found in knowledge base."
        
        context_parts = ["RELEVANT INFORMATION FROM KNOWLEDGE BASE:"]
        
        for i, doc in enumerate(documents, 1):
            source = doc.get("source", "Unknown")
            content = doc.get("content", "")
            
            # Highlight key fields based on document type
            if doc.get("type") == "faq":
                context_parts.append(f"\n[{i}] FAQ ({doc.get('category', 'General')}):")
                context_parts.append(f"Q: {doc.get('question', '')}")
                context_parts.append(f"A: {doc.get('answer', '')}")
            
            elif doc.get("type") == "service":
                context_parts.append(f"\n[{i}] Service: {doc.get('name', '')}")
                context_parts.append(f"Description: {doc.get('description', '')}")
            
            elif doc.get("type") == "pricing":
                context_parts.append(f"\n[{i}] Pricing Plan: {doc.get('name', '')}")
                context_parts.append(f"Price: {doc.get('price', '')}")
                context_parts.append(f"Description: {doc.get('description', '')}")
            
            elif doc.get("type") == "policy":
                context_parts.append(f"\n[{i}] Policy: {doc.get('title', '')}")
                context_parts.append(f"Summary: {doc.get('summary', '')}")
            
            else:
                context_parts.append(f"\n[{i}] {source}:")
                context_parts.append(content)
        
        return "\n".join(context_parts)
    
    def _assess_confidence(self, retrieved_docs: List[Dict[str, Any]], 
                          query: str) -> float:
        """
        Assess confidence in the response based on retrieved documents.
        
        Args:
            retrieved_docs: Retrieved documents
            query: Original query
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not retrieved_docs:
            return 0.0
        
        # Calculate average similarity score
        results = self.retriever.retrieve(query, top_k=len(retrieved_docs))
        if results:
            avg_score = sum(score for _, score in results) / len(results)
            # Normalize to 0.0-1.0 range
            return min(1.0, max(0.0, avg_score * 1.5))
        
        return 0.5
    
    def chat(self, user_message: str, include_history: bool = True) -> Dict[str, Any]:
        """
        Process user message and generate response using RAG.
        
        Args:
            user_message: The user's question/message
            include_history: Whether to include conversation history
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Check for empty message
            if not user_message or not user_message.strip():
                return {
                    "response": "Please ask a question or provide more details so I can assist you.",
                    "error": True,
                    "error_message": "Empty message",
                    "confidence": 0.0,
                    "retrieved_documents": [],
                    "sources": []
                }
            
            # Retrieve relevant documents
            retrieved_docs, scores = self.retrieve_context(
                user_message, 
                top_k=config.TOP_K_RESULTS
            )
            
            # Format context
            context = self._format_context(retrieved_docs)
            
            # Build messages for Groq API
            messages = [
                {
                    "role": "system",
                    "content": self._build_system_prompt()
                }
            ]
            
            # Add conversation history if enabled
            if include_history and self.conversation_history:
                messages.extend(self.conversation_history)
            
            # Add context and current message
            messages.append({
                "role": "user",
                "content": f"{context}\n\n---\n\nCustomer Question: {user_message}"
            })
            
            logger.debug(f"Sending request to Groq API with {len(messages)} messages")
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE,
                stream=False
            )
            
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_response
            })
            
            # Trim history to prevent token overflow
            self._trim_history()
            
            # Assess confidence
            confidence = self._assess_confidence(retrieved_docs, user_message)
            
            # Extract source documents
            sources = []
            for doc in retrieved_docs:
                sources.append({
                    "type": doc.get("type", "unknown"),
                    "source": doc.get("source", "Unknown"),
                    "id": doc.get("id", "")
                })
            
            logger.info(f"Generated response for user query (confidence: {confidence:.2f})")
            
            return {
                "response": assistant_response,
                "error": False,
                "confidence": confidence,
                "retrieved_documents": retrieved_docs,
                "sources": sources,
                "message_count": len(self.conversation_history) // 2
            }
        
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your question. Please try again or contact our support team.",
                "error": True,
                "error_message": str(e),
                "confidence": 0.0,
                "retrieved_documents": [],
                "sources": []
            }
    
    def _trim_history(self) -> None:
        """Trim conversation history to prevent token overflow"""
        # Estimate tokens (rough: 1 word ≈ 1.3 tokens)
        total_tokens = 0
        for msg in self.conversation_history:
            total_tokens += len(msg["content"].split()) * 1.3
        
        # Keep removing oldest messages if we exceed limit
        while total_tokens > config.MAX_HISTORY_TOKENS and len(self.conversation_history) > 2:
            removed = self.conversation_history.pop(0)
            total_tokens -= len(removed["content"].split()) * 1.3
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_summary(self) -> str:
        """
        Get a summary of the conversation so far.
        
        Returns:
            Summary string
        """
        if not self.conversation_history:
            return "No conversation history yet."
        
        summary_lines = []
        for i, msg in enumerate(self.conversation_history, 1):
            role = "Customer" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary_lines.append(f"{i}. {role}: {content}")
        
        return "\n".join(summary_lines)
    
    def handle_escalation(self, reason: str = "Complex issue requiring human assistance") -> Dict[str, Any]:
        """
        Handle escalation to human support.
        
        Args:
            reason: Reason for escalation
        
        Returns:
            Escalation information
        """
        contact_info = self.kb.get_contact_info()
        
        escalation_message = f"""
I understand you need assistance that requires a human touch. 

Here's how you can reach our support team:

📧 Email: {contact_info.get('email', 'support@techflow.com')}
📞 Phone: {contact_info.get('phone', '+1-800-TECHFLOW')}
💬 Live Chat: Available on our website {contact_info.get('website', '')}
🌐 Knowledge Base: {contact_info.get('support_channels', {}).get('knowledge_base', '')}

Hours of Operation: {contact_info.get('business_hours', 'Monday - Friday, 9 AM - 6 PM EST')}

Reason for escalation: {reason}

Our team will be happy to assist you further!
        """
        
        return {
            "response": escalation_message,
            "is_escalation": True,
            "contact_info": contact_info
        }
