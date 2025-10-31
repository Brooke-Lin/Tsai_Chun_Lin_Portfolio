from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

def get_fallback_response(question: str) -> str:
    """Enhanced fallback responses with better keyword matching"""
    fallback_responses = {
        "hello": "Hello! I'm Tsai Chun Lin's digital twin assistant. I'm here to help you learn about my background, skills, and experience. What would you like to know?",
        "experience": "I have experience in web development, particularly with React, Python, and full-stack applications. I recently graduated with a Master of Applied Information Technology from Victoria University, where I developed strong programming and problem-solving skills.",
        "skills": "My technical skills include Python, JavaScript, React, FastAPI, web development, AI/ML technologies, and database management. I'm passionate about creating user-friendly applications and have experience with both frontend and backend development.",
        "projects": "I've worked on various projects including interactive portfolio websites, multi-step forms, rating components, todo applications, and AI-powered digital twin systems. You can see examples of my work in the portfolio section.",
        "education": "I hold a Master of Applied Information Technology from Victoria University. During my studies, I focused on web development, programming fundamentals, and modern technology frameworks.",
        "background": "I'm a recent graduate passionate about technology and web development. I enjoy creating engaging user experiences and have a strong foundation in both frontend and backend technologies.",
        "contact": "You can reach me through the contact information provided in my portfolio. I'm always interested in discussing new opportunities and technology projects.",
        "about": "I'm Tsai Chun Lin, a recent graduate with a Master of Applied Information Technology from Victoria University. I'm passionate about web development and creating user-friendly applications."
    }
    
    question_lower = question.lower()
    
    # Check for greetings
    greetings = ["hello", "hi", "hey", "greetings", "how are you"]
    if any(greeting in question_lower for greeting in greetings):
        return fallback_responses["hello"]
    
    # Check for specific topics
    for key, response in fallback_responses.items():
        if key in question_lower or any(word in question_lower for word in key.split()):
            return response
    
    return "Thank you for your question! I'm a digital twin assistant representing Tsai Chun Lin. I can help you learn about my background, experience, technical skills, projects, and education. Feel free to ask about any aspect of my professional profile!"

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse URL and query parameters
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        try:
            # Get question parameter
            if 'question' not in query_params:
                response = {
                    "error": "Missing question parameter",
                    "answer": "Please provide a question parameter. For example: /api/chat?question=What is your experience?"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            question = query_params['question'][0].strip()
            
            if not question:
                response = {
                    "error": "Empty question",
                    "answer": "Please provide a valid question about my background, skills, or experience."
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Get response using fallback system
            answer = get_fallback_response(question)
            
            response = {
                "answer": answer,
                "source": "digital_twin_assistant"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                "error": "Internal server error",
                "answer": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or feel free to explore my portfolio and download my resume for more information about my background."
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()