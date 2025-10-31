from urllib.parse import parse_qs
import json
import os

# Fallback responses for when RAG isn't available
def get_fallback_response(question: str) -> str:
    fallback_responses = {
        "experience": "I have experience in web development, particularly with React, Python, and full-stack applications. I recently graduated with a Master of Applied Information Technology from Victoria University, where I developed strong programming and problem-solving skills.",
        "skills": "My technical skills include Python, JavaScript, React, FastAPI, web development, AI/ML technologies, and database management. I'm passionate about creating user-friendly applications and have experience with both frontend and backend development.",
        "projects": "I've worked on various projects including interactive portfolio websites, multi-step forms, rating components, todo applications, and AI-powered digital twin systems. You can see examples of my work in the portfolio section.",
        "education": "I hold a Master of Applied Information Technology from Victoria University. During my studies, I focused on web development, programming fundamentals, and modern technology frameworks.",
        "background": "I'm a recent graduate passionate about technology and web development. I enjoy creating engaging user experiences and have a strong foundation in both frontend and backend technologies.",
        "contact": "You can reach me through the contact information provided in my portfolio. I'm always interested in discussing new opportunities and technology projects.",
        "hello": "Hello! I'm Tsai Chun Lin's digital twin assistant. I'm here to help you learn about my background, skills, and experience. What would you like to know?",
        "about": "I'm Tsai Chun Lin, a recent graduate with a Master of Applied Information Technology from Victoria University. I'm passionate about web development and creating user-friendly applications."
    }
    
    question_lower = question.lower()
    
    # Check for greetings
    greetings = ["hello", "hi", "hey", "greetings"]
    if any(greeting in question_lower for greeting in greetings):
        return fallback_responses["hello"]
    
    # Check for specific topics
    for key, response in fallback_responses.items():
        if key in question_lower:
            return response
    
    return "Thank you for your question! I'm a digital twin assistant representing Tsai Chun Lin. I can help you learn about my background, experience, technical skills, projects, and education. Feel free to ask about any aspect of my professional profile!"

def handler(event, context):
    # Set CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({})
        }
    
    try:
        # Get query parameters
        query_params = event.get('queryStringParameters') or {}
        
        if not query_params or 'question' not in query_params:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({"error": "Missing question parameter"})
            }
        
        question = query_params['question']
        
        # Try to use RAG if available, otherwise use fallback
        try:
            # Try to import and use RAG function
            from digitaltwin_rg import get_rag_response
            answer = get_rag_response(question)
        except Exception as e:
            print(f"RAG not available, using fallback: {e}")
            answer = get_fallback_response(question)
        
        response_data = {"answer": answer}
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        print(f"Error in handler: {e}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                "error": "Internal server error",
                "answer": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or feel free to explore my portfolio and download my resume for more information about my background."
            })
        }