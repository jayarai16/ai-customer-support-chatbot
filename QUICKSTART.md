# Quick Start Guide - AI Customer Support Chatbot

Get the chatbot running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- Groq API key (free at https://console.groq.com)
- Modern web browser

## 🚀 5-Minute Setup

### Step 1: Download API Key
1. Go to https://console.groq.com
2. Sign up/Login (free account)
3. Create an API key
4. Copy it (you'll need it in Step 3)

### Step 2: Navigate to Project
```bash
cd chatbot_project
```

### Step 3: Create Environment File
```bash
# Create .env file with your API key
cat > .env << EOF
GROQ_API_KEY=paste_your_api_key_here
APP_NAME=AI Customer Support Chatbot
DEBUG=False
DATABASE_URL=sqlite:///./chatbot.db
HOST=0.0.0.0
PORT=8000
EOF
```

**On Windows**, create a file named `.env` in the project folder with:
```
GROQ_API_KEY=your_api_key_here
APP_NAME=AI Customer Support Chatbot
DEBUG=False
DATABASE_URL=sqlite:///./chatbot.db
HOST=0.0.0.0
PORT=8000
```

### Step 4: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install packages
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv groq scikit-learn numpy
```

### Step 5: Start Server
```bash
python -m app.main
```

You should see:
```
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 6: Open in Browser
Go to: **http://localhost:8000/static/index.html**

✅ **You're done!** The chatbot is ready to use.

---

## 🧪 Run Tests (Optional)

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Expected: 37 passed in ~1.5s
```

---

## 📚 Common Commands

### Check API Status
```bash
curl http://localhost:8000/health
```

### Stop the Server
Press `Ctrl+C` in the terminal

### View API Documentation
Open: http://localhost:8000/docs

### Change Port
Edit `.env` and set `PORT=8001` (or any port)

---

## 🐛 Troubleshooting

### API Key Error
```
ERROR: GROQ_API_KEY not set
```
**Solution**: Make sure `.env` file exists and has your API key

### Port Already in Use
```
Address already in use
```
**Solution**: Change PORT in `.env` or kill the process using port 8000

### ModuleNotFoundError
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Import Errors
Make sure you're running from the project root directory:
```bash
cd /path/to/chatbot_project
python -m app.main
```

---

## 📖 Example Conversations

### Try These Questions:
1. "What pricing plans do you offer?"
2. "How secure is my data?"
3. "What is your refund policy?"
4. "How do I create an account?"
5. "Does TechFlow integrate with Slack?"

### Features to Explore:
- 📋 **History Button** - View past conversations
- 🗑️ **Clear Button** - Start fresh
- ℹ️ **Info Button** - Learn about TechFlow
- 🤖 **Suggested Questions** - Click to try examples

---

## 🎯 What's Happening Behind the Scenes

```
You type a question
    ↓
API receives message
    ↓
TF-IDF retrieves 3 relevant documents
    ↓
Groq AI generates answer using context
    ↓
Response is stored in database
    ↓
Response appears on screen
```

---

## 📁 Project Structure

```
chatbot_project/
├── app/                 ← Backend code
├── static/              ← Frontend (HTML/CSS/JS)
├── data/                ← Knowledge base
├── tests/               ← Test suite
├── .env                 ← Your configuration (CREATE THIS)
├── requirements.txt     ← Dependencies
└── README.md           ← Full documentation
```

---

## 🔑 Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| GROQ_API_KEY | Your Groq API key | sk-xxxxx... |
| APP_NAME | Display name | AI Customer Support Chatbot |
| DEBUG | Debug mode (leave False) | False |
| PORT | Server port | 8000 |
| DATABASE_URL | Database file | sqlite:///./chatbot.db |

---

## 🌐 Accessing the Application

| URL | Purpose |
|-----|---------|
| http://localhost:8000/static/index.html | **Chat Interface** (use this!) |
| http://localhost:8000/docs | API Documentation |
| http://localhost:8000/health | Health Check |

---

## 💡 Pro Tips

1. **Keep terminal open** - The chatbot needs the server running
2. **Check API docs** - Visit /docs to explore all endpoints
3. **Read conversation history** - Click the history button to review chats
4. **Suggested questions** - Click them to try different topics

---

## 🎓 Next Steps

After setup:
1. Play with the chatbot interface
2. Ask various questions
3. Check the conversation history
4. Run the tests (`pytest tests/ -v`)
5. Read the full README for advanced features

---

## ❓ Need Help?

1. Check **README.md** for detailed documentation
2. Check **IMPLEMENTATION_REPORT.md** for technical details
3. Review test cases in **tests/test_chatbot.py** for examples
4. Check API docs at http://localhost:8000/docs

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Groq API key obtained
- [ ] `.env` file created with API key
- [ ] Dependencies installed
- [ ] Server started successfully
- [ ] Browser opens to chatbot interface
- [ ] Can type and send messages
- [ ] Receiving responses from chatbot

**If all checked, you're ready to go! 🎉**

---

## 📞 Quick Reference

```bash
# Complete setup
cd chatbot_project
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv groq scikit-learn numpy
echo "GROQ_API_KEY=your_key" > .env
python -m app.main
```

Then open: http://localhost:8000/static/index.html

**That's it! Enjoy the chatbot!** 🤖
