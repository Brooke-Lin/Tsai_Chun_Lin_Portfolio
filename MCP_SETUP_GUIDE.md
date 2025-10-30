# MCP Server Setup and Testing Guide

## Overview
Your Digital Twin MCP Server is now ready! This guide shows you how to test and integrate it with GitHub Copilot in VS Code Insiders.

## ✅ What We've Built

1. **Python MCP Server** (`digital_twin_mcp_server.py`)
   - Implements MCP protocol for tool-based interactions
   - Connects to your existing RAG system (Upstash Vector + Groq)
   - Provides 3 main tools: `ask_digital_twin`, `search_knowledge_base`, `get_server_status`

2. **Test Scripts**
   - `test_mcp_server.py` - Tests RAG functionality
   - `test_mcp_integration.py` - Tests MCP protocol integration
   - `start_mcp_server.py` - Easy startup script with environment checks

3. **VS Code Configuration**
   - `.vscode/settings.json` - MCP server configuration for VS Code

## 🚀 Quick Test Commands

### Test 1: Verify RAG System
```bash
python test_mcp_server.py
```
This tests your Groq + Upstash Vector integration.

### Test 2: Test MCP Protocol
```bash
python test_mcp_integration.py
```
This tests the MCP protocol communication.

### Test 3: Start MCP Server
```bash
python digital_twin_mcp_server.py
```
This starts the actual MCP server (stdio mode).

## 🔧 GitHub Copilot Integration

### Option 1: Direct MCP Server (Recommended)
Your server implements the MCP protocol directly. To use with GitHub Copilot:

1. **Ensure VS Code Insiders** with MCP support is installed
2. **Configure MCP in VS Code**:
   ```json
   // .vscode/settings.json already created
   {
     "mcpServers": {
       "digital-twin-mcp": {
         "command": "python",
         "args": ["digital_twin_mcp_server.py"],
         "env": { "PYTHONPATH": "." },
         "description": "Digital Twin RAG MCP Server"
       }
     }
   }
   ```

3. **Test with GitHub Copilot**:
   - Use `@workspace` prefix in Copilot Chat
   - Ask questions like: "What are my technical skills?"
   - Copilot will use your MCP server to answer

### Option 2: HTTP Wrapper (If MCP stdio doesn't work)
If direct stdio MCP doesn't work with your VS Code setup, we can create an HTTP wrapper.

## 🧪 Test Prompts for GitHub Copilot

Once integrated, try these prompts in GitHub Copilot Chat:

```
@workspace Tell me about my work experience using the digital twin data
```

```
@workspace What are my key technical skills according to my profile?
```

```
@workspace Help me prepare for a technical interview using my digital twin
```

```
@workspace What projects should I highlight based on my profile?
```

## 🐛 Troubleshooting

### Common Issues:

1. **"MCP package not found"**
   ```bash
   pip install mcp
   ```

2. **"GROQ_API_KEY not found"**
   - Check your `.env` file exists
   - Ensure `GROQ_API_KEY=your_key` is set

3. **"Vector database connection failed"**
   - Verify Upstash credentials in `.env`
   - Check `UPSTASH_VECTOR_REST_URL` and `UPSTASH_VECTOR_REST_TOKEN`

4. **GitHub Copilot not using MCP**
   - Ensure VS Code Insiders (not regular VS Code)
   - Check MCP is enabled in Copilot settings
   - Restart VS Code after MCP configuration
   - Use `@workspace` prefix in prompts

### Debug Commands:
```bash
# Check if server starts correctly
python digital_twin_mcp_server.py

# Test RAG independently  
python -c "from digitaltwin_rg import *; print(rag_query(setup_vector_database(), setup_groq_client(), 'Hello'))"

# Check environment
python -c "import os; print('GROQ_API_KEY:', bool(os.getenv('GROQ_API_KEY')))"
```

## 📊 Current Status

✅ **Working Components:**
- RAG system (Upstash Vector + Groq)
- MCP server implementation
- Tool-based query interface
- Environment configuration
- Test suite

⏳ **Next Steps:**
- Configure GitHub Copilot MCP integration in VS Code Insiders
- Test with actual Copilot prompts
- Optional: Add HTTP wrapper if needed

## 🎯 Success Criteria

Your MCP server is working correctly if:
1. `test_mcp_server.py` passes all tests ✅
2. `digital_twin_mcp_server.py` starts without errors ✅
3. GitHub Copilot can query your profile data using MCP ⏳

The core functionality is ready - the final step is connecting it to GitHub Copilot in VS Code Insiders!