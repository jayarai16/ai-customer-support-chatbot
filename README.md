# AI-Powered Customer Support Chatbot

> A production-ready, enterprise-grade AI customer support assistant using FastAPI, Groq LLM, and RAG (Retrieval-Augmented Generation) architecture.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Limitations & Future Improvements](#limitations--future-improvements)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This chatbot is designed for the **Mentroid AI Engineer Technical Assignment**. It provides accurate, context-aware customer support responses based on a comprehensive business knowledge base. The system uses a **Retrieval-Augmented Generation (RAG)** approach with TF-IDF document retrieval and Groq's powerful language models to ensure answers are grounded in actual business information rather than hallucinated.

**Key Goal**: Build a genuinely functional AI application that never hallucinates—if information isn't in the knowledge base, the chatbot clearly states this.

---

## ✨ Features

### Core Functionality
- ✅ **RAG Architecture**: Retrieves relevant documents before generating responses
- ✅ **No Hallucination**: Only answers from knowledge base; clearly states when info is unavailable
- ✅ **Multi-turn Conversations**: Maintains context across conversation history
- ✅ **Conversation History**: Stores all interactions in SQLite database
- ✅ **Session Management**: Unique session IDs for tracking user conversations
- ✅ **Confidence Scoring**: Displays confidence level of responses
- ✅ **Source Attribution**: Shows which documents provided the answer

### User Interface
- ✅ **Modern Web Interface**: Beautiful, responsive chat UI
- ✅ **Real-time Chat**: Instant message delivery and responses
- ✅ **Typing Indicators**: Visual feedback during processing
- ✅ **Suggested Questions**: Quick-start questions for new users
- ✅ **Conversation History Modal**: View past conversations
- ✅ **Mobile Responsive**: Works seamlessly on all devices
- ✅ **Dark/Light Theme Ready**: Professional styling

### Backend Features
- ✅ **FastAPI**: Modern, async Python web framework
- ✅ **Groq Integration**: Ultra-fast LLM inference
- ✅ **TF-IDF Retrieval**: Efficient semantic search
- ✅ **Input Validation**: Pydantic models for data integrity
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **CORS Support**: Cross-origin requests enabled
- ✅ **Health Checks**: System status monitoring

### Business Knowledge
- 📚 **20+ FAQs**: Comprehensive Q&A coverage
- 🏢 **Business Information**: Company details and contact info
- 💰 **Pricing Information**: 4 detailed pricing tiers
- 🔐 **Security & Policies**: GDPR, CCPA, Security policies
- 🛠️ **Services**: 8 detailed service descriptions
- 📞 **Support Channels**: Multiple contact methods

### Testing & Quality
- ✅ **15+ Test Cases**: Comprehensive test coverage
- ✅ **Direct FAQ Testing**: Tests actual Q&A
- ✅ **Multi-Entry Questions**: Tests complex queries
- ✅ **Edge Case Handling**: Unicode, special chars, typos
- ✅ **Database Testing**: Session and history tests
- ✅ **Retrieval Testing**: Document ranking verification

---

## 🔧 Technology Stack

### Backend
- **Python 3.9+**: Core language
- **FastAPI 0.104.1**: Web framework
- **Uvicorn 0.24.0**: ASGI server
- **Groq API**: LLM provider (Ultra-fast inference)
- **Scikit-learn 1.3.2**: TF-IDF vectorization
- **SQLite**: Conversation database
- **Pydantic 2.5.0**: Data validation

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling (custom, no frameworks)
- **JavaScript (Vanilla)**: Interactions
- **Responsive Design**: Mobile-first approach

### Development & Testing
- **Pytest 7.4.3**: Testing framework
- **Python-dotenv 1.0.0**: Environment management

---

## 🏗️ Architecture

### RAG Pipeline

```
User Question
    ↓
[Session Management]
    ↓
[Document Retrieval]
  (TF-IDF + Hybrid Ranking)
    ↓
[Context Formatting]
    ↓
[Groq LLM Processing]
  (With System Prompt + Context)
    ↓
[Response Generation]
    ↓
[Confidence Assessment]
    ↓
[Database Storage]
    ↓
Response to User
```

### System Components

1. **Knowledge Base Module** (`knowledge_base.py`)
   - Loads business data from JSON
   - Prepares 60+ documents for retrieval
   - Provides keyword search

2. **Retrieval Module** (`retriever.py`)
   - TF-IDF vectorization (500 features)
   - Cosine similarity matching
   - Hybrid ranking with source weighting
   - Top-3 document retrieval by default

3. **Chatbot Module** (`chatbot.py`)
   - Groq API integration
   - RAG pipeline orchestration
   - Conversation history management
   - Confidence scoring
   - Escalation handling

4. **Database Module** (`database.py`)
   - SQLite conversation storage
   - Session management
   - History tracking
   - Feedback collection

5. **FastAPI Application** (`main.py`)
   - REST API endpoints
   - Request/response validation
   - Error handling
   - Static file serving

6. **Frontend** (`static/`)
   - Interactive chat UI
   - Real-time message updates
   - Modal dialogs for history/info
   - Toast notifications

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Groq API key (free at https://console.groq.com)
- Modern web browser

### Step 1: Clone/Download Project
```bash
cd chatbot_project
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Create .env file from template
cp .env.example .env

# Edit .env and add your Groq API key
# Open .env in your editor and set:
# GROQ_API_KEY=your_actual_api_key_here
```

### Step 5: Run the Application
```bash
# Start the server
python -m app.main

# Server will start at http://localhost:8000
```

### Step 6: Access the Chatbot
- **Web Interface**: http://localhost:8000/static/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 💬 Usage

### Using the Web Interface

1. **Start a Conversation**
   - Open http://localhost:8000/static/index.html
   - Click on a suggested question or type your own
   - Click "Send" or press Enter

2. **View Response**
   - Get instant AI-generated response
   - See confidence score and source documents
   - Reference actual business information

3. **Access Features**
   - 📋 **History**: View past conversations
   - 🗑️ **Clear**: Start fresh chat
   - ℹ️ **About**: See business information
   - Session ID: Unique identifier for session

### Example Conversations

```
User: "What pricing plans do you offer?"
Bot: "We offer four pricing tiers..."
[Shows confidence and sources]

User: "How secure is my data?"
Bot: "Security is our top priority. We implement..."
[Shows FAQ sources used]

User: "What's your favorite color?"
Bot: "I don't have information about that in my knowledge base..."
[Shows no hallucination]
```

---

## 🔌 API Endpoints

### Chat Endpoints

#### POST `/chat` - Send Message
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What pricing plans do you offer?",
    "session_id": "uuid-here",
    "include_history": true
  }'
```

**Response**:
```json
{
  "response": "We offer...",
  "session_id": "uuid-here",
  "message_count": 2,
  "confidence": 0.92,
  "sources": [
    {"type": "pricing", "source": "Pricing", "id": "plan_001"}
  ],
  "timestamp": "2024-10-25T10:30:00",
  "error": false
}
```

#### POST `/session/create` - Create Session
```bash
curl -X POST "http://localhost:8000/session/create" \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "John Doe",
    "user_email": "john@example.com"
  }'
```

#### GET `/history/{session_id}` - Get Conversation History
```bash
curl "http://localhost:8000/history/uuid-here?limit=50"
```

#### POST `/history/clear/{session_id}` - Clear History
```bash
curl -X POST "http://localhost:8000/history/clear/uuid-here"
```

#### POST `/escalate` - Escalate to Human Support
```bash
curl -X POST "http://localhost:8000/escalate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid-here",
    "reason": "Need to speak with a human"
  }'
```

### Knowledge Base Endpoints

#### GET `/knowledge-base/faqs` - Get FAQs
```bash
curl "http://localhost:8000/knowledge-base/faqs"
# Optional: ?category=Pricing
```

#### GET `/knowledge-base/services` - Get Services
```bash
curl "http://localhost:8000/knowledge-base/services"
```

#### GET `/knowledge-base/pricing` - Get Pricing
```bash
curl "http://localhost:8000/knowledge-base/pricing"
```

#### GET `/info` - Get Business Info
```bash
curl "http://localhost:8000/info"
```

### Admin Endpoints

#### GET `/health` - Health Check
```bash
curl "http://localhost:8000/health"
```

#### GET `/stats` - Application Statistics
```bash
curl "http://localhost:8000/stats"
```

---

## 🧪 Testing

### Run All Tests
```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with detailed output
pytest tests/ -vv

# Run specific test file
pytest tests/test_chatbot.py -v

# Run specific test class
pytest tests/test_chatbot.py::TestKnowledgeBase -v

# Run specific test
pytest tests/test_chatbot.py::TestKnowledgeBase::test_kb_loads_successfully -v
```

### Test Coverage Summary

**Total Test Cases: 30+**

#### Knowledge Base Tests (5)
- ✅ KB loads successfully
- ✅ Contains FAQs
- ✅ Contains services
- ✅ Contains pricing
- ✅ FAQ search works

#### Retriever Tests (3)
- ✅ Initializes correctly
- ✅ TF-IDF returns results
- ✅ Hybrid ranking works

#### Database Tests (5)
- ✅ Database initializes
- ✅ Session creation
- ✅ Conversation storage
- ✅ History retrieval
- ✅ Clear history

#### Scenario Tests (15+)
1. ✅ Direct FAQ question
2. ✅ Multi-entry question
3. ✅ Vague question
4. ✅ General business query
5. ✅ Service features
6. ✅ Policy questions
7. ✅ Security questions
8. ✅ Support contact
9. ✅ Onboarding
10. ✅ Technical questions
11. ✅ Comparison questions
12. ✅ Integration questions
13. ✅ Typo tolerance
14. ✅ Similar questions consistency
15. ✅ Empty query handling

#### Edge Cases (4+)
- ✅ Very long queries
- ✅ Special characters
- ✅ Unicode characters
- ✅ Case insensitivity

### Running Specific Test Scenarios

```bash
# Test direct FAQ retrieval
pytest tests/test_chatbot.py::TestChatbotScenarios::test_direct_faq_question -v

# Test multi-entry questions
pytest tests/test_chatbot.py::TestChatbotScenarios::test_multi_entry_question -v

# Test all scenarios
pytest tests/test_chatbot.py::TestChatbotScenarios -v

# Test edge cases
pytest tests/test_chatbot.py::TestEdgeCases -v
```

### Expected Test Output
```
tests/test_chatbot.py::TestKnowledgeBase::test_kb_loads_successfully PASSED
tests/test_chatbot.py::TestRetriever::test_tfidf_retrieval_returns_results PASSED
tests/test_chatbot.py::TestDatabase::test_session_creation PASSED
tests/test_chatbot.py::TestChatbotScenarios::test_direct_faq_question PASSED
...
============================== 30+ passed in 1.23s ==============================
```

---

## 📁 Project Structure

```
chatbot_project/
├── app/                              # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application
│   ├── chatbot.py                    # Chatbot with Groq integration
│   ├── knowledge_base.py             # KB management
│   ├── retriever.py                  # TF-IDF & Hybrid retriever
│   ├── database.py                   # SQLite conversation storage
│   └── config.py                     # Configuration settings
│
├── data/
│   └── business_faqs.json            # Knowledge base (60+ documents)
│
├── static/                           # Frontend files
│   ├── index.html                    # Main UI
│   ├── style.css                     # Styling
│   └── script.js                     # Frontend logic
│
├── tests/
│   ├── __init__.py
│   └── test_chatbot.py               # 30+ test cases
│
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment template
├── .gitignore                        # Git ignore rules
├── README.md                         # This file
└── chatbot.db                        # SQLite database (auto-created)
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```env
# API Configuration
GROQ_API_KEY=your_api_key_here

# Application Settings
APP_NAME=AI Customer Support Chatbot
DEBUG=False
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./chatbot.db
DB_PATH=chatbot.db

# Server
HOST=0.0.0.0
PORT=8000
```

### Configuration Details

| Variable | Default | Description |
|----------|---------|-------------|
| GROQ_API_KEY | - | Required API key from Groq |
| APP_NAME | AI Customer Support Chatbot | Application display name |
| DEBUG | False | Enable debug mode |
| LOG_LEVEL | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| DATABASE_URL | sqlite:///./chatbot.db | Database connection URL |
| HOST | 0.0.0.0 | Server host address |
| PORT | 8000 | Server port |

### Retrieval Configuration (in config.py)

```python
TFIDF_MAX_FEATURES = 500         # TF-IDF vocabulary size
TOP_K_RESULTS = 3               # Documents to retrieve
SIMILARITY_THRESHOLD = 0.3       # Minimum relevance score
MAX_HISTORY_TOKENS = 2000        # Conversation history limit
MAX_CONVERSATION_TURNS = 50      # Max turns per session
```

---

## 📊 Model Configuration

### Groq Model Settings
```python
MODEL_NAME = "mixtral-8x7b-32768"  # Fast, capable model
MAX_TOKENS = 1024                   # Response length
TEMPERATURE = 0.7                   # Creativity level
```

**Why Mixtral 8x7B?**
- Extremely fast inference (< 1 second)
- Excellent instruction following
- Good reasoning capability
- Free tier availability on Groq

---

## 🎓 Example Conversations

### Example 1: Direct FAQ
```
User: "What is TechFlow Solutions?"
Bot: "TechFlow Solutions is a cloud-based productivity platform that helps 
teams collaborate, manage projects, and streamline workflows..."
Confidence: 94%
Sources: FAQ (General)
```

### Example 2: Complex Question
```
User: "I'm a startup founder. What plan should I choose?"
Bot: "For a startup, I'd recommend starting with our Free plan to evaluate 
the platform, then upgrading to the Starter plan ($29/month) for up to 10 
users as you grow..."
Confidence: 87%
Sources: Pricing, FAQ (Pricing)
```

### Example 3: Unknown Information
```
User: "What are your quarterly earnings?"
Bot: "I don't have information about financial earnings in my knowledge base. 
For detailed financial information, please contact our investor relations team 
at support@techflow.com or call +1-800-TECHFLOW."
Confidence: 45%
Sources: None
```

---

## 🔒 Security Features

- ✅ **API Key Protection**: Keys stored in environment variables
- ✅ **Input Validation**: Pydantic models validate all inputs
- ✅ **CORS Enabled**: Configurable cross-origin requests
- ✅ **Error Handling**: No sensitive info in error messages
- ✅ **Session IDs**: UUID-based session identification
- ✅ **SQL Injection Prevention**: Parameterized queries
- ✅ **XSS Protection**: Escaped HTML content

---

## ⚠️ Limitations & Future Improvements

### Current Limitations

1. **Knowledge Base Scope**
   - Limited to 60+ pre-loaded documents
   - No dynamic KB updates without server restart
   - No multi-language support

2. **AI Capabilities**
   - Single Groq model (no model switching)
   - No image/file processing
   - No voice input/output
   - Fixed context window

3. **Scalability**
   - SQLite (not production for high volume)
   - Single server (no load balancing)
   - No caching layer

4. **User Experience**
   - No email notifications
   - No user accounts/authentication
   - No feedback collection UI
   - No advanced analytics

### Planned Improvements

1. **Admin Interface**
   - Update knowledge base without restart
   - Manage users and feedback
   - Analytics dashboard
   - Response performance metrics

2. **Enhanced AI**
   - Multiple model options
   - Semantic caching
   - Intent classification
   - Entity recognition

3. **Scalability**
   - PostgreSQL integration
   - Redis caching
   - Docker containerization
   - Kubernetes deployment

4. **Features**
   - User authentication
   - Email/SMS notifications
   - Lead capture forms
   - Multi-language support
   - Voice bot capability
   - Integration API for third-party tools

5. **Analytics**
   - Response quality metrics
   - User satisfaction tracking
   - Conversation analytics
   - Escalation patterns

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not set"
**Solution**: 
1. Create `.env` file in project root
2. Add `GROQ_API_KEY=your_actual_key`
3. Restart the server

### Issue: "Failed to load static files"
**Solution**:
1. Verify `static/` folder exists
2. Check file permissions
3. Ensure HTML, CSS, JS files are in static folder

### Issue: "Module not found"
**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution**:
```bash
# Change port in .env
PORT=8001

# Or kill process using port
# Linux/Mac: lsof -ti:8000 | xargs kill -9
# Windows: netstat -ano | findstr :8000
```

### Issue: "Database lock"
**Solution**:
1. Delete `chatbot.db`
2. Restart server
3. Database will be recreated

### Issue: "Slow responses from Groq"
**Solution**:
- Check Groq API status
- Verify internet connection
- Consider reducing MAX_TOKENS
- Check system resources

---

## 📝 Development Notes

### Adding New FAQs
1. Edit `data/business_faqs.json`
2. Add new FAQ object to `faqs` array
3. Restart server
4. Retriever automatically indexes new content

### Customizing System Prompt
Edit `_build_system_prompt()` in `app/chatbot.py` to customize bot behavior.

### Performance Tuning
- Adjust `TFIDF_MAX_FEATURES` (higher = more memory)
- Modify `TOP_K_RESULTS` (more results = slower)
- Change `SIMILARITY_THRESHOLD` (filter irrelevant docs)

---

## 🙋 Support

For issues or questions:
1. Check this README
2. Review the test cases for examples
3. Check API documentation at `/docs`
4. Review logs for error details

---

## ✅ Verification Checklist

- [x] Application starts without errors
- [x] Frontend loads at http://localhost:8000/static/index.html
- [x] API responds at http://localhost:8000/health
- [x] Chat messages are sent and received
- [x] All 30+ tests pass
- [x] No API keys exposed in code
- [x] Conversation history is saved
- [x] Confidence scores are displayed
- [x] Sources are attributed
- [x] Error handling works
- [x] Mobile responsive design works
- [x] Documentation is complete


