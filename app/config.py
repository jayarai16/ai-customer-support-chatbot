"""
Configuration settings for the chatbot application.
Loads environment variables with secure defaults.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration settings"""
    
    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "AI Customer Support Chatbot")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")
    DB_PATH: str = os.getenv("DB_PATH", "chatbot.db")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Knowledge Base Configuration
    KB_PATH: Path = Path(__file__).parent.parent / "data" / "business_faqs.json"
    
    # Model Configuration
    MODEL_NAME: str = "mixtral-8x7b-32768"  # Groq's fast model
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.7
    
    # Retrieval Configuration
    TFIDF_MAX_FEATURES: int = 500
    TOP_K_RESULTS: int = 3
    SIMILARITY_THRESHOLD: float = 0.3
    
    # Session Configuration
    MAX_HISTORY_TOKENS: int = 2000
    MAX_CONVERSATION_TURNS: int = 50
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if not cls.GROQ_API_KEY:
            print("WARNING: GROQ_API_KEY not set. Please set it in .env file")
            return False
        return True


# Create config instance
config = Config()
