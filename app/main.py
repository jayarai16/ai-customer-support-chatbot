"""
Main FastAPI Application
Provides REST API endpoints for the customer support chatbot.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from app.config import config
from app.knowledge_base import KnowledgeBase
from app.chatbot import GroqChatbot
from app.database import ConversationDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
if not config.validate():
    logger.error("Configuration validation failed. Please check your .env file.")

# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description="AI-Powered Customer Support Chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
try:
    knowledge_base = KnowledgeBase(config.KB_PATH)
    chatbot = GroqChatbot(knowledge_base)
    database = ConversationDatabase(config.DB_PATH)
    logger.info("Application components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

# Mount static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, 
                         description="User's message/question")
    session_id: Optional[str] = Field(None, description="Session ID (auto-generated if not provided)")
    include_history: Optional[bool] = Field(True, description="Include conversation history")
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or whitespace only')
        return v.strip()


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    session_id: str
    message_count: int
    confidence: float
    sources: List[dict]
    timestamp: str
    error: bool = False
    error_message: Optional[str] = None


class SessionRequest(BaseModel):
    """Request model for session creation"""
    user_name: Optional[str] = Field(None, max_length=100)
    user_email: Optional[str] = Field(None, max_length=100)
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    """Response model for session"""
    session_id: str
    created_at: str
    user_info: Optional[dict]


class HistoryRequest(BaseModel):
    """Request model for history retrieval"""
    session_id: str
    limit: Optional[int] = Field(50, le=100, description="Max conversations to retrieve")


class EscalationRequest(BaseModel):
    """Request model for escalation"""
    session_id: str
    reason: str = Field(..., max_length=1000, description="Reason for escalation")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    version: str
    components: dict


# ==================== Endpoints ====================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - redirects to documentation"""
    return {
        "message": "Welcome to AI Customer Support Chatbot",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "knowledge_base": "loaded" if knowledge_base.documents else "empty",
            "chatbot": "ready",
            "database": "connected"
        }
    }


@app.post("/session/create", response_model=SessionResponse, tags=["Session"])
async def create_session(request: SessionRequest):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        user_info = None
        
        if request.user_name or request.user_email:
            user_info = {
                "name": request.user_name,
                "email": request.user_email,
                "metadata": request.metadata
            }
        
        database.create_session(session_id, user_info)
        
        return {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "user_info": user_info
        }
    
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Chat endpoint - process user message and return chatbot response.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Ensure session exists
        session = database.get_session(session_id)
        if not session:
            database.create_session(session_id)
        
        # Process message with chatbot
        result = chatbot.chat(request.message, include_history=request.include_history)
        
        # Prepare sources for response
        sources = result.get("sources", [])
        
        # Store conversation in database
        background_tasks.add_task(
            database.add_conversation,
            session_id=session_id,
            user_message=request.message,
            assistant_response=result["response"],
            retrieved_docs=result.get("retrieved_documents", []),
            confidence_score=result.get("confidence", 0.0)
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=session_id,
            message_count=result.get("message_count", 0),
            confidence=result.get("confidence", 0.0),
            sources=sources,
            timestamp=datetime.utcnow().isoformat(),
            error=result.get("error", False),
            error_message=result.get("error_message")
        )
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing request")


@app.post("/escalate", tags=["Support"])
async def escalate(request: EscalationRequest):
    """Escalate to human support"""
    try:
        result = chatbot.handle_escalation(request.reason)
        
        # Store escalation in database
        database.add_conversation(
            session_id=request.session_id,
            user_message=f"ESCALATION REQUEST: {request.reason}",
            assistant_response=result["response"],
            confidence_score=1.0
        )
        
        return {
            "success": True,
            "message": result["response"],
            "contact_info": result["contact_info"]
        }
    
    except Exception as e:
        logger.error(f"Error processing escalation: {e}")
        raise HTTPException(status_code=500, detail="Error processing escalation")


@app.get("/history/{session_id}", tags=["History"])
async def get_history(session_id: str, limit: int = 50):
    """Get conversation history for a session"""
    try:
        history = database.get_conversation_history(session_id, limit)
        return {
            "session_id": session_id,
            "conversation_count": len(history),
            "conversations": history
        }
    
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving history")


@app.post("/history/clear/{session_id}", tags=["History"])
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    try:
        success = database.clear_session_history(session_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to clear history")
        
        return {
            "success": True,
            "message": f"History cleared for session {session_id}"
        }
    
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail="Error clearing history")


@app.get("/knowledge-base/categories", tags=["Knowledge Base"])
async def get_categories():
    """Get all FAQ categories"""
    try:
        categories = knowledge_base.get_all_faq_categories()
        return {
            "categories": categories,
            "count": len(categories)
        }
    
    except Exception as e:
        logger.error(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving categories")


@app.get("/knowledge-base/faqs", tags=["Knowledge Base"])
async def get_faqs(category: Optional[str] = None):
    """Get FAQs, optionally filtered by category"""
    try:
        if category:
            faqs = knowledge_base.get_faqs_by_category(category)
        else:
            faqs = knowledge_base.kb_data.get("faqs", [])
        
        return {
            "count": len(faqs),
            "faqs": faqs
        }
    
    except Exception as e:
        logger.error(f"Error retrieving FAQs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving FAQs")


@app.get("/knowledge-base/services", tags=["Knowledge Base"])
async def get_services():
    """Get all services"""
    try:
        services = knowledge_base.get_services()
        return {
            "count": len(services),
            "services": services
        }
    
    except Exception as e:
        logger.error(f"Error retrieving services: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving services")


@app.get("/knowledge-base/pricing", tags=["Knowledge Base"])
async def get_pricing():
    """Get pricing tiers"""
    try:
        pricing = knowledge_base.get_pricing()
        return {
            "count": len(pricing),
            "pricing_tiers": pricing
        }
    
    except Exception as e:
        logger.error(f"Error retrieving pricing: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving pricing")


@app.get("/knowledge-base/contact", tags=["Knowledge Base"])
async def get_contact():
    """Get contact information"""
    try:
        contact = knowledge_base.get_contact_info()
        return contact
    
    except Exception as e:
        logger.error(f"Error retrieving contact info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving contact info")


@app.get("/stats", tags=["Admin"])
async def get_stats():
    """Get application statistics"""
    try:
        stats = database.get_statistics()
        return {
            **stats,
            "knowledge_base_documents": len(knowledge_base.get_documents()),
            "faq_count": len(knowledge_base.kb_data.get("faqs", []))
        }
    
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving stats")


@app.get("/info", tags=["Info"])
async def get_info():
    """Get business information"""
    try:
        return knowledge_base.get_business_info()
    
    except Exception as e:
        logger.error(f"Error retrieving business info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving info")


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        },
    )


# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info(f"Starting {config.APP_NAME}")
    logger.info(f"Knowledge base loaded with {len(knowledge_base.get_documents())} documents")
    logger.info(f"Database: {config.DB_PATH}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info(f"Shutting down {config.APP_NAME}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.HOST,
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )
