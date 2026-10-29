"""
Knowledge Base Management Module
Loads and manages the business information from JSON source.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    Manages the business knowledge base including FAQs, services, pricing, and policies.
    Provides methods to access and search through the knowledge base.
    """
    
    def __init__(self, kb_path: Path):
        """
        Initialize the knowledge base from JSON file.
        
        Args:
            kb_path: Path to the knowledge base JSON file
        """
        self.kb_path = kb_path
        self.kb_data: Dict[str, Any] = {}
        self.documents: List[Dict[str, str]] = []
        self.load()
    
    def load(self) -> None:
        """Load knowledge base from JSON file"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                self.kb_data = json.load(f)
            logger.info(f"Knowledge base loaded from {self.kb_path}")
            self._prepare_documents()
        except FileNotFoundError:
            logger.error(f"Knowledge base file not found: {self.kb_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing knowledge base JSON: {e}")
            raise
    
    def _prepare_documents(self) -> None:
        """
        Prepare all documents for retrieval.
        Converts FAQs, services, pricing, and policies into searchable documents.
        """
        self.documents = []
        
        # Add FAQs
        if "faqs" in self.kb_data:
            for faq in self.kb_data["faqs"]:
                doc = {
                    "id": faq.get("id", ""),
                    "type": "faq",
                    "category": faq.get("category", ""),
                    "content": f"{faq.get('question', '')} {faq.get('answer', '')}",
                    "question": faq.get("question", ""),
                    "answer": faq.get("answer", ""),
                    "source": "FAQ"
                }
                self.documents.append(doc)
        
        # Add Services
        if "services" in self.kb_data:
            for service in self.kb_data["services"]:
                features_text = " ".join(service.get("features", []))
                doc = {
                    "id": service.get("id", ""),
                    "type": "service",
                    "content": f"{service.get('name', '')} {service.get('description', '')} {features_text}",
                    "name": service.get("name", ""),
                    "description": service.get("description", ""),
                    "source": "Service"
                }
                self.documents.append(doc)
        
        # Add Pricing Information
        if "pricing_tiers" in self.kb_data:
            for plan in self.kb_data["pricing_tiers"]:
                features_text = " ".join(plan.get("features", []))
                doc = {
                    "id": plan.get("id", ""),
                    "type": "pricing",
                    "content": f"{plan.get('name', '')} {plan.get('price', '')} {plan.get('description', '')} {features_text}",
                    "name": plan.get("name", ""),
                    "price": plan.get("price", ""),
                    "description": plan.get("description", ""),
                    "source": "Pricing"
                }
                self.documents.append(doc)
        
        # Add Policies
        if "policies" in self.kb_data:
            for policy in self.kb_data["policies"]:
                key_points = " ".join(policy.get("key_points", []))
                doc = {
                    "id": policy.get("id", ""),
                    "type": "policy",
                    "content": f"{policy.get('title', '')} {policy.get('summary', '')} {key_points}",
                    "title": policy.get("title", ""),
                    "summary": policy.get("summary", ""),
                    "source": "Policy"
                }
                self.documents.append(doc)
        
        logger.info(f"Prepared {len(self.documents)} documents for retrieval")
    
    def get_documents(self) -> List[Dict[str, str]]:
        """Get all documents in the knowledge base"""
        return self.documents
    
    def get_faq_by_id(self, faq_id: str) -> Optional[Dict[str, Any]]:
        """Get FAQ by ID"""
        for faq in self.kb_data.get("faqs", []):
            if faq.get("id") == faq_id:
                return faq
        return None
    
    def get_faqs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get FAQs by category"""
        return [faq for faq in self.kb_data.get("faqs", []) 
                if faq.get("category") == category]
    
    def get_business_info(self) -> Dict[str, Any]:
        """Get general business information"""
        return self.kb_data.get("business_info", {})
    
    def get_contact_info(self) -> Dict[str, Any]:
        """Get contact information"""
        return self.kb_data.get("contact", {})
    
    def get_services(self) -> List[Dict[str, Any]]:
        """Get all services"""
        return self.kb_data.get("services", [])
    
    def get_pricing(self) -> List[Dict[str, Any]]:
        """Get all pricing tiers"""
        return self.kb_data.get("pricing_tiers", [])
    
    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all policies"""
        return self.kb_data.get("policies", [])
    
    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Simple keyword search through FAQs.
        Returns matching FAQs.
        """
        keyword_lower = keyword.lower()
        results = []
        
        for faq in self.kb_data.get("faqs", []):
            question = faq.get("question", "").lower()
            answer = faq.get("answer", "").lower()
            category = faq.get("category", "").lower()
            
            if (keyword_lower in question or 
                keyword_lower in answer or 
                keyword_lower in category):
                results.append(faq)
        
        return results
    
    def get_all_faq_categories(self) -> List[str]:
        """Get all unique FAQ categories"""
        categories = set()
        for faq in self.kb_data.get("faqs", []):
            category = faq.get("category")
            if category:
                categories.add(category)
        return sorted(list(categories))
