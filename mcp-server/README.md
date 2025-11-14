# Digital Twin MCP Server

A Model Context Protocol (MCP) server that provides AI-powered tools for knowledge retrieval, file summarization, data updates, and calculations for your digital twin portfolio assistant.

## 🚀 Features

### 📊 **4 Core MCP Tools:**

1. **🔍 retrieve_knowledge** - Semantic search through portfolio data using RAG
2. **📄 summarize_file** - AI-powered file summarization using Groq
3. **📝 update_portfolio_data** - Add, update, or delete portfolio Q&A data  
4. **🧮 perform_calculation** - Math, statistics, and computational tools

## 🛠️ Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- Existing RAG system with Upstash Vector + Groq API keys

### Quick Start

1. **Install Dependencies:**
   ```bash
   cd mcp-server
   npm install
   ```

2. **Start MCP Server:**
   ```bash
   ./mcp-manager.sh start
   ```

3. **Or use the helper script:**
   ```bash
   ./mcp-manager.sh install  # Install dependencies
   ./mcp-manager.sh start    # Start server
   ```

## 🔧 Configuration

### Environment Variables
The server uses your existing `.env` files:
- `GROQ_API_KEY` - For AI summarization and calculations
- `UPSTASH_VECTOR_REST_URL` - For knowledge retrieval
- `UPSTASH_VECTOR_REST_TOKEN` - For vector database access

### MCP Client Setup (Claude Desktop)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "digital-twin": {
      "command": "node",
      "args": ["/path/to/your/project/mcp-server/index.js"]
    }
  }
}
```

## 📖 Tool Usage Examples

### 1. Knowledge Retrieval
```json
{
  "name": "retrieve_knowledge",
  "arguments": {
    "query": "What are your technical skills?",
    "topK": 3
  }
}
```

### 2. File Summarization
```json
{
  "name": "summarize_file",
  "arguments": {
    "filePath": "api/chat.py",
    "maxLength": 150
  }
}
```

### 3. Update Portfolio Data
```json
{
  "name": "update_portfolio_data",
  "arguments": {
    "action": "add",
    "data": {
      "question": "Do you have experience with React?",
      "answer": "Yes, I'm currently learning React.js and have built several practice projects."
    }
  }
}
```

### 4. Perform Calculations
```json
{
  "name": "perform_calculation",
  "arguments": {
    "type": "statistics",
    "expression": "Calculate statistics for project completion rates",
    "data": [85, 92, 78, 95, 88, 91, 87]
  }
}
```

## 🏗️ Architecture

```
Digital Twin MCP Server
├── Knowledge Retrieval (RAG Integration)
│   ├── Vector Search via Upstash
│   ├── Fallback to Direct Search
│   └── Integration with chat.py API
│
├── File Summarization (Groq AI)
│   ├── File Reading & Processing  
│   ├── AI Summarization via Groq
│   └── Configurable Summary Length
│
├── Data Management
│   ├── Portfolio Q&A CRUD Operations
│   ├── JSON File Management
│   └── Vector Database Refresh Hints
│
└── Calculations
    ├── Mathematical Expressions
    ├── Statistical Analysis
    ├── Financial Calculations (Future)
    └── Programming Utils (Future)
```

## 🔗 Integration with Existing System

The MCP server integrates seamlessly with your existing infrastructure:

- **RAG System**: Calls your `chat.py` API for knowledge retrieval
- **Portfolio Data**: Manages your `portfolio-info.json` file
- **Environment**: Uses your existing `.env` configuration
- **Vector DB**: Works with your Upstash Vector setup

## 🧪 Testing

Test individual tools using Claude Desktop or any MCP client:

1. **Knowledge Retrieval Test:**
   - Ask: "What projects have you worked on?"
   - Should return RAG-enhanced responses

2. **File Summary Test:**
   - Summarize: `api/digitaltwin_rg.py`
   - Should return AI-generated summary

3. **Data Update Test:**
   - Add new Q&A pair about a skill
   - Verify in `portfolio-info.json`

4. **Calculation Test:**
   - Calculate statistics for an array
   - Perform math expressions

## 📁 Files Created

- `mcp-server/index.js` - Main MCP server implementation
- `mcp-server/package.json` - Node.js dependencies
- `mcp-config.json` - MCP server configuration
- `mcp-manager.sh` - Management script
- `mcp-server/README.md` - This documentation

## 🚀 Next Steps

1. **Install and test** the MCP server
2. **Configure Claude Desktop** to use your server
3. **Test each tool** with real queries
4. **Extend calculations** for financial/programming needs
5. **Add more file formats** for summarization

## 🔍 Troubleshooting

- **Server won't start**: Check Node.js version and dependencies
- **Knowledge retrieval fails**: Ensure `chat.py` API is running
- **Summarization errors**: Verify `GROQ_API_KEY` in environment
- **File not found**: Use relative paths from project root

---

Your digital twin now has powerful MCP capabilities! 🤖✨