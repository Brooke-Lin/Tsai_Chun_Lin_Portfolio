#!/bin/bash

# Digital Twin MCP Server Setup and Management Script

PROJECT_ROOT="/Users/brookelin/Desktop/Tsai Chun Lin-profolio-test"
MCP_DIR="$PROJECT_ROOT/mcp-server"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE} Digital Twin MCP Server Manager${NC}"
    echo -e "${BLUE}================================${NC}"
}

install_dependencies() {
    echo -e "${YELLOW}📦 Installing MCP server dependencies...${NC}"
    cd "$MCP_DIR"
    
    if command -v npm &> /dev/null; then
        npm install
        echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
    else
        echo -e "${RED}❌ npm not found. Please install Node.js first.${NC}"
        exit 1
    fi
}

start_server() {
    echo -e "${YELLOW}🚀 Starting MCP server...${NC}"
    cd "$MCP_DIR"
    
    # Check if dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Dependencies not found. Installing...${NC}"
        install_dependencies
    fi
    
    echo -e "${BLUE}🤖 MCP Server starting on stdio...${NC}"
    echo -e "${BLUE}📋 Available tools:${NC}"
    echo -e "   - retrieve_knowledge: Search portfolio data"
    echo -e "   - summarize_file: AI file summarization"
    echo -e "   - update_portfolio_data: Manage portfolio data"
    echo -e "   - perform_calculation: Math and statistics"
    
    npm start
}

test_server() {
    echo -e "${YELLOW}🧪 Testing MCP server functionality...${NC}"
    
    # Test knowledge retrieval
    echo -e "${BLUE}Testing knowledge retrieval...${NC}"
    # This would typically involve using MCP client tools
    
    echo -e "${GREEN}✅ Server tests would run here${NC}"
    echo -e "${YELLOW}💡 Use Claude Desktop or MCP client to test tools${NC}"
}

show_usage() {
    echo -e "${YELLOW}Usage: $0 [command]${NC}"
    echo ""
    echo -e "${BLUE}Commands:${NC}"
    echo "  install    - Install dependencies"
    echo "  start      - Start the MCP server"
    echo "  test       - Test server functionality"
    echo "  help       - Show this help message"
    echo ""
    echo -e "${BLUE}MCP Tools Available:${NC}"
    echo "  🔍 retrieve_knowledge   - Search portfolio with RAG"
    echo "  📄 summarize_file       - AI file summarization"
    echo "  📝 update_portfolio_data - Manage Q&A data"
    echo "  🧮 perform_calculation  - Math & statistics"
}

# Main script logic
print_header

case "${1:-help}" in
    "install")
        install_dependencies
        ;;
    "start")
        start_server
        ;;
    "test")
        test_server
        ;;
    "help"|*)
        show_usage
        ;;
esac