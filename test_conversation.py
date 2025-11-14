#!/usr/bin/env python3

"""
Test script for the improved Digital Twin RAG system
Tests conversation quality and smart question handling
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from digitaltwin_rg import setup_groq_client, setup_vector_database, rag_query

def test_conversation_improvements():
    """Test the improved conversational abilities"""
    print("🧪 Testing Improved Digital Twin Conversation")
    print("=" * 50)
    
    # Initialize clients
    groq_client = setup_groq_client()
    index = setup_vector_database()
    
    if not groq_client or not index:
        print("❌ Failed to initialize RAG system")
        return
    
    # Test cases
    test_questions = [
        {
            "category": "❌ Personal Questions (Should Decline Politely)",
            "questions": [
                "what is your age?",
                "How old are you?",
                "what is your gender?",
                "Are you male or female?",
                "Are you single or married?"
            ]
        },
        {
            "category": "✅ Professional Questions (Should Answer Well)", 
            "questions": [
                "What is your education background?",
                "Tell me about your technical skills?", 
                "What projects have you worked on?",
                "What are your career goals?"
            ]
        },
        {
            "category": "🤔 Out-of-Scope Questions (Should Redirect)",
            "questions": [
                "What's the weather like?",
                "Do you like pizza?",
                "What's your favorite movie?"
            ]
        }
    ]
    
    for test_group in test_questions:
        print(f"\n{test_group['category']}")
        print("-" * 40)
        
        for question in test_group['questions']:
            print(f"\n❓ Question: {question}")
            try:
                response = rag_query(index, groq_client, question)
                print(f"🤖 Response: {response}")
            except Exception as e:
                print(f"❌ Error: {e}")
            print()
    
    print("🎯 Test completed! Check responses above to verify improvements.")

if __name__ == "__main__":
    test_conversation_improvements()