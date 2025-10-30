# 🤖 Frontend Chat Setup Guide

## Quick Start (2 minutes)

Your digital twin chat is now ready! Just follow these steps:

### 1. Start the Backend API (if not running)
```bash
uvicorn digitaltwin_api:app --reload --port 8001
```

### 2. Start the Frontend Server (if not running)
```bash
python -m http.server 3000
```

### 3. Open Your Portfolio
Go to: **http://localhost:3000**

### 4. Test the Chat
1. Click the **chat button** (bottom right corner)
2. Ask questions like:
   - "What are your technical skills?"
   - "Tell me about your education"
   - "What projects have you worked on?"
   - "What is your work experience?"

## ✅ What Works Now

Your chat interface connects to your digital twin RAG system and can answer questions about:
- **Technical Skills**: Python, JavaScript, PHP, HTML, CSS, etc.
- **Education**: Victoria University, University of Queensland
- **Projects**: Book 2 Drive App, portfolio projects
- **Work Experience**: Ben Cutains internship, current barista role
- **Career Goals**: Frontend/full-stack development aspirations

## 🧪 Quick Test

Run this to verify everything is working:
```bash
python test_frontend_chat.py
```

## 🛠️ Troubleshooting

### Chat Not Responding?
1. Check API is running: `curl http://127.0.0.1:8001/ask?question=hello`
2. Check browser console for errors (F12)
3. Make sure you're using `http://localhost:3000` (not `file://`)

### CORS Errors?
- Always access via `http://localhost:3000`
- Don't open the HTML file directly in browser

### API Errors?
```bash
# Restart API server
uvicorn digitaltwin_api:app --reload --port 8001
```

## 🎯 How It Works

1. **User types question** → Frontend (JavaScript)
2. **JavaScript sends request** → API (`http://127.0.0.1:8001/ask`)
3. **API processes question** → RAG system (Upstash Vector + Groq)
4. **RAG returns answer** → API → Frontend
5. **Answer displayed** → Chat interface

## 📁 Key Files

- `index.html` - Your portfolio with chat interface
- `script.js` - Chat JavaScript (enhanced with error handling)
- `digitaltwin_api.py` - FastAPI server
- `digitaltwin_rg.py` - RAG logic (Upstash + Groq)
- `digitaltwin.json` - Your profile data

## 🚀 Your Chat is Ready!

Visit **http://localhost:3000** and start chatting with your digital twin! 🎉