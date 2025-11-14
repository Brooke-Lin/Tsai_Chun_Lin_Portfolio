#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config({ path: '../.env' });
dotenv.config({ path: '../api/.env' });

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class DigitalTwinMCPServer {
  constructor() {
    this.server = new Server(
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

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'retrieve_knowledge',
            description: 'Retrieve knowledge from the portfolio vector database using semantic search',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Search query to find relevant portfolio information'
                },
                topK: {
                  type: 'number',
                  description: 'Number of top results to return (default: 3)',
                  default: 3
                }
              },
              required: ['query']
            }
          },
          {
            name: 'summarize_file',
            description: 'Summarize the contents of a file using AI',
            inputSchema: {
              type: 'object',
              properties: {
                filePath: {
                  type: 'string',
                  description: 'Path to the file to summarize (relative to project root)'
                },
                maxLength: {
                  type: 'number',
                  description: 'Maximum length of summary in words (default: 200)',
                  default: 200
                }
              },
              required: ['filePath']
            }
          },
          {
            name: 'update_portfolio_data',
            description: 'Update portfolio data and refresh vector embeddings',
            inputSchema: {
              type: 'object',
              properties: {
                action: {
                  type: 'string',
                  enum: ['add', 'update', 'delete'],
                  description: 'Action to perform on the data'
                },
                data: {
                  type: 'object',
                  description: 'Data to add or update (for Q&A format: {question, answer})'
                },
                id: {
                  type: 'string',
                  description: 'ID for update or delete operations'
                }
              },
              required: ['action']
            }
          },
          {
            name: 'perform_calculation',
            description: 'Perform various calculations and computations',
            inputSchema: {
              type: 'object',
              properties: {
                type: {
                  type: 'string',
                  enum: ['math', 'statistics', 'financial', 'programming'],
                  description: 'Type of calculation to perform'
                },
                expression: {
                  type: 'string',
                  description: 'Mathematical expression or calculation description'
                },
                data: {
                  type: 'array',
                  description: 'Array of numbers for statistical calculations',
                  items: { type: 'number' }
                }
              },
              required: ['type', 'expression']
            }
          }
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'retrieve_knowledge':
            return await this.retrieveKnowledge(args);
          case 'summarize_file':
            return await this.summarizeFile(args);
          case 'update_portfolio_data':
            return await this.updatePortfolioData(args);
          case 'perform_calculation':
            return await this.performCalculation(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        console.error(`Error in tool ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool ${name}: ${error.message}`
        );
      }
    });
  }

  setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error('[MCP Error]', error);
    };

    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async retrieveKnowledge(args) {
    const { query, topK = 3 } = args;

    try {
      // Use fetch to call our existing RAG API
      const response = await fetch(`http://localhost:8000/api/chat.py`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          request_id: `mcp-${Date.now()}`
        })
      });

      if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
      }

      const data = await response.json();

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              query: query,
              answer: data.answer,
              source: 'RAG Vector Search',
              timestamp: new Date().toISOString()
            }, null, 2)
          }
        ]
      };

    } catch (error) {
      // Fallback: try to read portfolio data directly
      try {
        const portfolioPath = path.join(__dirname, '../portfolio-info.json');
        const portfolioData = JSON.parse(await fs.readFile(portfolioPath, 'utf-8'));
        
        // Simple text search as fallback
        const matches = portfolioData.filter(item => 
          item.question.toLowerCase().includes(query.toLowerCase()) ||
          item.answer.toLowerCase().includes(query.toLowerCase())
        ).slice(0, topK);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                query: query,
                matches: matches,
                source: 'Direct Portfolio Search (Fallback)',
                note: 'RAG API unavailable, using direct search',
                timestamp: new Date().toISOString()
              }, null, 2)
            }
          ]
        };

      } catch (fallbackError) {
        throw new Error(`Knowledge retrieval failed: ${error.message}. Fallback also failed: ${fallbackError.message}`);
      }
    }
  }

  async summarizeFile(args) {
    const { filePath, maxLength = 200 } = args;

    try {
      // Read file content
      const fullPath = path.join(__dirname, '..', filePath);
      const content = await fs.readFile(fullPath, 'utf-8');

      // Use Groq for summarization
      const groqApiKey = process.env.GROQ_API_KEY;
      if (!groqApiKey) {
        throw new Error('GROQ_API_KEY not found in environment variables');
      }

      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${groqApiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-3.1-8b-instant',
          messages: [
            {
              role: 'system',
              content: `You are a helpful assistant that summarizes file contents. Provide a concise summary in approximately ${maxLength} words.`
            },
            {
              role: 'user',
              content: `Please summarize this file content:\n\n${content.substring(0, 4000)}`
            }
          ],
          max_tokens: Math.ceil(maxLength * 1.5),
          temperature: 0.3
        })
      });

      if (!response.ok) {
        throw new Error(`Groq API call failed: ${response.statusText}`);
      }

      const data = await response.json();
      const summary = data.choices[0]?.message?.content || 'Summary generation failed';

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              filePath: filePath,
              summary: summary,
              fileSize: content.length,
              timestamp: new Date().toISOString()
            }, null, 2)
          }
        ]
      };

    } catch (error) {
      throw new Error(`File summarization failed: ${error.message}`);
    }
  }

  async updatePortfolioData(args) {
    const { action, data, id } = args;

    try {
      const portfolioPath = path.join(__dirname, '../portfolio-info.json');
      let portfolioData = JSON.parse(await fs.readFile(portfolioPath, 'utf-8'));

      let result = {};

      switch (action) {
        case 'add':
          if (!data || !data.question || !data.answer) {
            throw new Error('Add action requires data with question and answer fields');
          }
          portfolioData.push(data);
          result = { action: 'added', data: data, totalItems: portfolioData.length };
          break;

        case 'update':
          if (!id || !data) {
            throw new Error('Update action requires id and data fields');
          }
          const updateIndex = portfolioData.findIndex(item => 
            item.question.toLowerCase().includes(id.toLowerCase())
          );
          if (updateIndex === -1) {
            throw new Error(`Item with id "${id}" not found`);
          }
          portfolioData[updateIndex] = { ...portfolioData[updateIndex], ...data };
          result = { action: 'updated', id: id, data: portfolioData[updateIndex] };
          break;

        case 'delete':
          if (!id) {
            throw new Error('Delete action requires id field');
          }
          const deleteIndex = portfolioData.findIndex(item => 
            item.question.toLowerCase().includes(id.toLowerCase())
          );
          if (deleteIndex === -1) {
            throw new Error(`Item with id "${id}" not found`);
          }
          const deletedItem = portfolioData.splice(deleteIndex, 1)[0];
          result = { action: 'deleted', deletedItem: deletedItem, totalItems: portfolioData.length };
          break;

        default:
          throw new Error(`Unknown action: ${action}`);
      }

      // Save updated data
      await fs.writeFile(portfolioPath, JSON.stringify(portfolioData, null, 2), 'utf-8');

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              ...result,
              timestamp: new Date().toISOString(),
              note: 'Portfolio data updated. Remember to refresh vector embeddings by running the digitaltwin_rg.py script.'
            }, null, 2)
          }
        ]
      };

    } catch (error) {
      throw new Error(`Portfolio data update failed: ${error.message}`);
    }
  }

  async performCalculation(args) {
    const { type, expression, data } = args;

    try {
      let result = {};

      switch (type) {
        case 'math':
          // Safe evaluation of mathematical expressions
          const mathResult = this.evaluateMathExpression(expression);
          result = { type: 'math', expression: expression, result: mathResult };
          break;

        case 'statistics':
          if (!data || !Array.isArray(data)) {
            throw new Error('Statistics calculations require a data array');
          }
          result = {
            type: 'statistics',
            data: data,
            results: this.calculateStatistics(data)
          };
          break;

        case 'financial':
          result = { type: 'financial', expression: expression, result: 'Financial calculations not implemented yet' };
          break;

        case 'programming':
          result = { type: 'programming', expression: expression, result: 'Programming calculations not implemented yet' };
          break;

        default:
          throw new Error(`Unknown calculation type: ${type}`);
      }

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              ...result,
              timestamp: new Date().toISOString()
            }, null, 2)
          }
        ]
      };

    } catch (error) {
      throw new Error(`Calculation failed: ${error.message}`);
    }
  }

  evaluateMathExpression(expression) {
    // Basic safe math evaluation
    // Remove any non-mathematical characters for security
    const sanitized = expression.replace(/[^0-9+\-*/.() ]/g, '');
    
    try {
      // Use Function constructor for safe evaluation
      const result = Function(`"use strict"; return (${sanitized})`)();
      return result;
    } catch (error) {
      throw new Error(`Invalid mathematical expression: ${expression}`);
    }
  }

  calculateStatistics(data) {
    const sorted = [...data].sort((a, b) => a - b);
    const n = data.length;
    const sum = data.reduce((acc, val) => acc + val, 0);
    const mean = sum / n;
    
    const variance = data.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);
    
    const median = n % 2 === 0 
      ? (sorted[n/2 - 1] + sorted[n/2]) / 2 
      : sorted[Math.floor(n/2)];

    return {
      count: n,
      sum: sum,
      mean: mean,
      median: median,
      min: Math.min(...data),
      max: Math.max(...data),
      variance: variance,
      standardDeviation: stdDev,
      range: Math.max(...data) - Math.min(...data)
    };
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Digital Twin MCP Server running on stdio');
  }
}

const server = new DigitalTwinMCPServer();
server.run().catch(console.error);