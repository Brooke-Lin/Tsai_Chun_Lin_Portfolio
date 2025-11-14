#!/usr/bin/env node

/**
 * Digital Twin MCP Server
 * Enables AI assistants to access your professional profile via RAG
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { Index } from '@upstash/vector';
import Groq from 'groq-sdk';
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';

// Load environment variables from parent directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const parentDir = dirname(__dirname);
dotenv.config({ path: join(parentDir, '.env') });

// Global clients
let groqClient = null;
let vectorIndex = null;

// Initialize Groq client
function initializeGroq() {
  if (!process.env.GROQ_API_KEY) {
    console.error("❌ GROQ_API_KEY not found");
    return null;
  }
  
  try {
    groqClient = new Groq({ apiKey: process.env.GROQ_API_KEY });
    console.log("✅ Groq client initialized");
    return groqClient;
  } catch (error) {
    console.error("❌ Groq init error:", error.message);
    return null;
  }
}

// Initialize Upstash Vector
function initializeVector() {
  try {
    vectorIndex = new Index({
      url: process.env.UPSTASH_VECTOR_REST_URL,
      token: process.env.UPSTASH_VECTOR_REST_TOKEN,
    });
    console.log("✅ Upstash Vector initialized");
    return vectorIndex;
  } catch (error) {
    console.error("❌ Vector init error:", error.message);
    return null;
  }
}

// Perform RAG query
async function performRAG(question) {
  try {
    console.log('🔍 Searching for:', question);
    
    const results = await vectorIndex.query({
      data: question,
      topK: 3,
      includeMetadata: true,
    });
    
    if (!results || results.length === 0) {
      return "I don't have specific information about that topic.";
    }
    
    const context = results
      .map(result => {
        const metadata = result.metadata || {};
        const content = metadata.content || '';
        return content;
      })
      .filter(Boolean)
      .join('\n\n');
    
    if (!context) {
      return "I found some information but couldn't extract details.";
    }
    
    const prompt = `Based on this information about yourself, answer the question as Tsai Chun Lin in first person:

Context: ${context}

Question: ${question}

Response:`;
    
    console.log("⚡ Generating response...");
    
    const completion = await groqClient.chat.completions.create({
      model: "llama-3.1-8b-instant",
      messages: [
        {
          role: "system",
          content: "You are Tsai Chun Lin's digital twin. Answer as if you are Tsai, speaking in first person about your background and experience."
        },
        {
          role: "user", 
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 500,
    });
    
    return completion.choices[0]?.message?.content?.trim() || "I couldn't generate a response.";
    
  } catch (error) {
    console.error("❌ RAG error:", error.message);
    return "Error processing your question: " + error.message;
  }
}

// Create MCP server
const server = new Server(
  {
    name: 'digital-twin-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'ask_digital_twin',
        description: 'Ask questions about Tsai Chun Lin\'s professional background and experience',
        inputSchema: {
          type: 'object',
          properties: {
            question: {
              type: 'string',
              description: 'Question about professional background, skills, or experience',
            },
          },
          required: ['question'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'ask_digital_twin') {
    if (!args.question) {
      throw new McpError(ErrorCode.InvalidParams, 'Question is required');
    }

    const answer = await performRAG(args.question);
    
    return {
      content: [
        {
          type: 'text',
          text: answer,
        },
      ],
    };
  }

  throw new McpError(ErrorCode.MethodNotFound, 'Unknown tool: ' + name);
});

// Start server
async function main() {
  console.log("🤖 Digital Twin MCP Server Starting...");
  
  const groq = initializeGroq();
  const vector = initializeVector();
  
  if (!groq || !vector) {
    console.error("❌ Failed to initialize clients");
    process.exit(1);
  }
  
  console.log("✅ MCP Server ready!");
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.log("🔗 MCP Server listening...");
}

main().catch((error) => {
  console.error("❌ Server error:", error);
  process.exit(1);
});
