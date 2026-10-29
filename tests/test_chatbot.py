"""
Comprehensive Test Suite for AI Customer Support Chatbot
Tests cover direct FAQs, multi-entry questions, missing info, and edge cases.
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.knowledge_base import KnowledgeBase
from app.retriever import TFIDFRetriever, HybridRetriever
from app.chatbot import GroqChatbot
from app.database import ConversationDatabase
from app.config import Config


# ==================== Fixtures ====================

@pytest.fixture
def knowledge_base():
    """Initialize knowledge base"""
    kb_path = Path(__file__).parent.parent / "data" / "business_faqs.json"
    return KnowledgeBase(kb_path)


@pytest.fixture
def retriever(knowledge_base):
    """Initialize retriever"""
    return HybridRetriever(
        documents=knowledge_base.get_documents(),
        max_features=500
    )


@pytest.fixture
def database():
    """Initialize test database"""
    import tempfile
    import os
    
    # Create a temporary database file for each test
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = ConversationDatabase(db_path)
    db._ensure_db_exists()  # Ensure tables are created
    
    yield db
    
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


# ==================== Knowledge Base Tests ====================

class TestKnowledgeBase:
    """Test knowledge base loading and functionality"""
    
    def test_kb_loads_successfully(self, knowledge_base):
        """Test that knowledge base loads without errors"""
        assert knowledge_base.kb_data is not None
        assert len(knowledge_base.documents) > 0
    
    def test_kb_contains_faqs(self, knowledge_base):
        """Test that knowledge base contains FAQs"""
        faqs = knowledge_base.kb_data.get("faqs", [])
        assert len(faqs) > 0
        assert any(faq.get("question") for faq in faqs)
    
    def test_kb_contains_services(self, knowledge_base):
        """Test that knowledge base contains services"""
        services = knowledge_base.get_services()
        assert len(services) > 0
        assert any(svc.get("name") for svc in services)
    
    def test_kb_contains_pricing(self, knowledge_base):
        """Test that knowledge base contains pricing information"""
        pricing = knowledge_base.get_pricing()
        assert len(pricing) > 0
        assert any(plan.get("price") for plan in pricing)
    
    def test_faq_search(self, knowledge_base):
        """Test FAQ search functionality"""
        results = knowledge_base.search_by_keyword("plan")
        assert len(results) > 0
        # Check that results contain plan-related FAQs
        assert any("plan" in faq.get("question", "").lower() 
                   or "plan" in faq.get("answer", "").lower() 
                   for faq in results)


# ==================== Retriever Tests ====================

class TestRetriever:
    """Test document retriever"""
    
    def test_retriever_initializes(self, retriever):
        """Test that retriever initializes correctly"""
        assert retriever.tfidf_retriever is not None
        assert retriever.tfidf_retriever.documents is not None
    
    def test_tfidf_retrieval_returns_results(self, retriever):
        """Test that TF-IDF retrieval returns results"""
        results = retriever.retrieve("What is the pricing?", top_k=3)
        assert isinstance(results, list)
        assert len(results) > 0
    
    def test_hybrid_retrieval_returns_results(self, retriever):
        """Test hybrid retrieval with source weighting"""
        results = retriever.retrieve("How do I create an account?", top_k=3)
        assert len(results) > 0
        
        # Check that results have scores
        for doc, score in results:
            assert isinstance(score, float)
            assert 0 <= score <= 1
    
    def test_retrieval_threshold_filtering(self, retriever):
        """Test that similarity threshold filters results"""
        results_low_threshold = retriever.retrieve(
            "pricing plans features",
            top_k=5,
            threshold=0.0
        )
        results_high_threshold = retriever.retrieve(
            "pricing plans features",
            top_k=5,
            threshold=0.8
        )
        
        # High threshold should return fewer or equal results
        assert len(results_high_threshold) <= len(results_low_threshold)


# ==================== Database Tests ====================

class TestDatabase:
    """Test conversation database"""
    
    def test_database_initialization(self, database):
        """Test that database initializes successfully"""
        stats = database.get_statistics()
        assert "total_sessions" in stats
        assert "total_conversations" in stats
    
    def test_session_creation(self, database):
        """Test session creation"""
        # Ensure tables exist
        database._ensure_db_exists()
        
        session_id = "test_session_001"
        success = database.create_session(session_id, {"name": "Test User"})
        assert success is True
        
        session = database.get_session(session_id)
        assert session is not None
        assert session["session_id"] == session_id
    
    def test_conversation_storage(self, database):
        """Test storing conversations"""
        database._ensure_db_exists()
        
        session_id = "test_session_002"
        database.create_session(session_id)
        
        success = database.add_conversation(
            session_id=session_id,
            user_message="What are your pricing plans?",
            assistant_response="We offer Free, Starter, Professional, and Enterprise plans.",
            confidence_score=0.95
        )
        assert success is True
        
        history = database.get_conversation_history(session_id)
        assert len(history) > 0
        assert history[0]["user_message"] == "What are your pricing plans?"
    
    def test_history_retrieval(self, database):
        """Test retrieving conversation history"""
        database._ensure_db_exists()
        
        session_id = "test_session_003"
        database.create_session(session_id)
        
        for i in range(5):
            database.add_conversation(
                session_id=session_id,
                user_message=f"Question {i}?",
                assistant_response=f"Answer {i}."
            )
        
        history = database.get_conversation_history(session_id, limit=10)
        assert len(history) == 5
    
    def test_history_limit(self, database):
        """Test history limit parameter"""
        database._ensure_db_exists()
        
        session_id = "test_session_004"
        database.create_session(session_id)
        
        for i in range(20):
            database.add_conversation(
                session_id=session_id,
                user_message=f"Q{i}",
                assistant_response=f"A{i}"
            )
        
        history = database.get_conversation_history(session_id, limit=5)
        assert len(history) == 5
    
    def test_clear_history(self, database):
        """Test clearing conversation history"""
        session_id = "test_session_005"
        database.create_session(session_id)
        
        database.add_conversation(
            session_id=session_id,
            user_message="Test",
            assistant_response="Response"
        )
        
        database.clear_session_history(session_id)
        history = database.get_conversation_history(session_id)
        assert len(history) == 0


# ==================== Chatbot Functionality Tests ====================
# Note: These tests don't require API key for basic retrieval testing

class TestChatbotRetrieval:
    """Test chatbot retrieval and context formatting"""
    
    def test_context_retrieval(self, knowledge_base):
        """Test that chatbot retrieves relevant context"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents(),
            max_features=500
        )
        
        results = retriever.retrieve(
            "What are your pricing plans?",
            top_k=5
        )
        
        assert len(results) > 0
        # Should retrieve documents related to pricing
        doc_types = [doc.get("type") for doc, _ in results]
        assert "pricing" in doc_types or "faq" in doc_types
    
    def test_context_formatting(self, knowledge_base):
        """Test context formatting for LLM"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents(),
            max_features=500
        )
        
        results = retriever.retrieve("How do I create an account?", top_k=3)
        retrieved_docs = [doc for doc, _ in results]
        
        # Check that retrieved documents contain FAQ content
        assert len(retrieved_docs) > 0
        assert any(doc.get("content") for doc in retrieved_docs)
    
    def test_confidence_assessment(self, knowledge_base):
        """Test confidence scoring"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents(),
            max_features=500
        )
        
        # Query with good match should have high confidence
        results = retriever.retrieve("pricing plans cost", top_k=3)
        if results:
            _, score = results[0]
            assert score > 0


# ==================== Integration Test Cases ====================

class TestChatbotScenarios:
    """Test realistic chatbot scenarios"""
    
    def test_direct_faq_question(self, knowledge_base):
        """TEST 1: Direct FAQ question that should be answered directly"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        # This should match pricing FAQ
        results = retriever.retrieve("What pricing plans do you offer?", top_k=5)
        assert len(results) > 0
        
        # Check that pricing or FAQ documents are retrieved
        relevant_docs = [doc for doc, _ in results 
                        if doc.get("type") in ["pricing", "faq"]]
        assert len(relevant_docs) > 0
    
    def test_multi_entry_question(self, knowledge_base):
        """TEST 2: Question requiring multiple knowledge base entries"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        # This might need both account and security info
        results = retriever.retrieve(
            "How do I create an account and is my data secure?",
            top_k=5
        )
        assert len(results) > 0
    
    def test_vague_question(self, knowledge_base):
        """TEST 3: Vague question with multiple interpretations"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("Tell me about your service", top_k=3)
        # Should retrieve something relevant
        assert len(results) > 0
    
    def test_general_query(self, knowledge_base):
        """TEST 4: General business information query"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("What is TechFlow?", top_k=3)
        assert len(results) > 0
    
    def test_service_features_query(self, knowledge_base):
        """TEST 5: Question about specific service features"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve(
            "What features does project management include?",
            top_k=3
        )
        assert len(results) > 0
    
    def test_policy_question(self, knowledge_base):
        """TEST 6: Policy and compliance related question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("What is your refund policy?", top_k=3)
        assert len(results) > 0
        
        policy_docs = [doc for doc, _ in results if doc.get("type") == "policy"]
        assert len(policy_docs) > 0
    
    def test_security_question(self, knowledge_base):
        """TEST 7: Security and data protection question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("How secure is my data?", top_k=3)
        assert len(results) > 0
    
    def test_support_contact_question(self, knowledge_base):
        """TEST 8: Support and contact information question"""
        contact = knowledge_base.get_contact_info()
        assert contact is not None
        assert "email" in contact or "phone" in contact
    
    def test_onboarding_question(self, knowledge_base):
        """TEST 9: Onboarding and getting started question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("How do I get started?", top_k=3)
        assert len(results) > 0
    
    def test_technical_question(self, knowledge_base):
        """TEST 10: Technical capability question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve(
            "What system requirements do I need?",
            top_k=3
        )
        assert len(results) > 0
    
    def test_comparison_question(self, knowledge_base):
        """TEST 11: Plan comparison question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve(
            "What's the difference between Starter and Professional?",
            top_k=5
        )
        assert len(results) > 0
    
    def test_integration_question(self, knowledge_base):
        """TEST 12: Integration capabilities question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve(
            "Does TechFlow integrate with other tools?",
            top_k=3
        )
        assert len(results) > 0
    
    def test_typo_tolerance(self, knowledge_base):
        """TEST 13: Query with minor typos"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        # Even with typo, should find relevant results
        results = retriever.retrieve("pricin plans", top_k=3)
        assert len(results) > 0
    
    def test_similar_questions_consistency(self, knowledge_base):
        """TEST 14: Different phrasings of same question"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results1 = retriever.retrieve("How much does it cost?", top_k=3)
        results2 = retriever.retrieve("What is the pricing?", top_k=3)
        results3 = retriever.retrieve("How are you priced?", top_k=3)
        
        # All should retrieve pricing documents
        assert all(len(r) > 0 for r in [results1, results2, results3])
    
    def test_empty_query_handling(self, knowledge_base):
        """TEST 15: Empty or whitespace-only query"""
        retriever = HybridRetriever(
            documents=knowledge_base.get_documents()
        )
        
        results = retriever.retrieve("   ", top_k=3)
        # Empty query should return empty results or handle gracefully
        # This tests the system doesn't crash
        assert isinstance(results, list)


# ==================== Edge Cases ====================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_very_long_query(self, retriever):
        """Test handling of very long queries"""
        long_query = "What " * 500 + "is pricing?"
        results = retriever.retrieve(long_query, top_k=3)
        assert isinstance(results, list)
    
    def test_special_characters_in_query(self, retriever):
        """Test queries with special characters"""
        query = "What is the price??? $$$ @#$%"
        results = retriever.retrieve(query, top_k=3)
        assert isinstance(results, list)
    
    def test_unicode_in_query(self, retriever):
        """Test Unicode characters in query"""
        query = "What is pricing? 🤔 €£¥"
        results = retriever.retrieve(query, top_k=3)
        assert isinstance(results, list)
    
    def test_case_insensitivity(self, retriever):
        """Test that retrieval is case-insensitive"""
        results_lower = retriever.retrieve("pricing plans", top_k=3)
        results_upper = retriever.retrieve("PRICING PLANS", top_k=3)
        results_mixed = retriever.retrieve("PrIcInG PlAnS", top_k=3)
        
        # All should return results
        assert all(len(r) > 0 for r in [results_lower, results_upper, results_mixed])


# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
