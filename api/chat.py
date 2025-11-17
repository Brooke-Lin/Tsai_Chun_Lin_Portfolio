"""
Chat API Server - Backend for AI Chat Box

This file creates a Python HTTP server that powers the AI chat functionality:

Architecture:
Frontend (script.js) → HTTP Request → chat.py → RAG System → AI Response

Key Features:
1. HTTP API endpoint for chat requests
2. Integration with RAG system (digitaltwin_rag.py)
3. Rate limiting and caching for performance
4. Fallback systems for reliability
5. CORS support for web browser requests

API Usage:
GET /api/chat?question=What are your skills?
Returns: {"answer": "I have experience with...", "source": "rag_system"}
"""

# Import standard Python libraries
from http.server import BaseHTTPRequestHandler  # For creating HTTP server
import json                                     # For JSON data handling
import urllib.parse                            # For URL parameter parsing
import os                                      # For file system operations
import time                                    # For rate limiting timestamps
from collections import defaultdict            # For rate limiting data structure

# Import the RAG system from parent directory
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # Add parent dir to Python path

# Try to import RAG system with graceful fallback
try:
    # Import RAG functions from digitaltwin_rag.py
    from digitaltwin_rag import setup_groq_client, setup_vector_database, rag_query
    RAG_AVAILABLE = True
    print("✅ Course-compliant RAG system loaded successfully")
    
    # Global variables for RAG clients (initialized once for performance)
    RAG_GROQ_CLIENT = None  # Groq AI client
    RAG_INDEX = None        # Vector database index
    
    def initialize_rag():
        """
        Initialize RAG System Components
        
        What this does:
        1. Sets up Groq AI client for response generation
        2. Sets up Upstash Vector database for information retrieval
        3. Caches clients globally to avoid repeated initialization
        
        Performance optimization: Initialize once, use many times
        """
        global RAG_GROQ_CLIENT, RAG_INDEX
        
        # Only initialize if not already done
        if RAG_GROQ_CLIENT is None or RAG_INDEX is None:
            print("🔄 Initializing RAG system...")
            RAG_GROQ_CLIENT = setup_groq_client()      # Initialize AI client
            RAG_INDEX = setup_vector_database()        # Initialize vector DB
            
            if RAG_GROQ_CLIENT and RAG_INDEX:
                print("✅ RAG system initialized successfully!")
            else:
                print("❌ Failed to initialize RAG system")
        
        return RAG_GROQ_CLIENT, RAG_INDEX
    
except ImportError as e:
    # Graceful fallback if RAG system not available
    print(f"⚠️ RAG system not available: {e}")
    print("📋 Falling back to direct JSON responses")
    RAG_AVAILABLE = False
    RAG_GROQ_CLIENT = None
    RAG_INDEX = None
    
    def initialize_rag():
        """Fallback function when RAG system not available"""
        return None, None

# Performance and Security Systems

# In-memory cache to store recent responses (prevents duplicate AI calls)
request_cache = {}                    # Stores: {question: (timestamp, response)}
rate_limit_cache = defaultdict(list)  # Stores: {ip_address: [timestamp1, timestamp2, ...]}

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60        # Time window in seconds (1 minute)
RATE_LIMIT_REQUESTS = 10      # Maximum requests per IP per window

def check_rate_limit(ip_address):
    """
    Implement Rate Limiting to Prevent Abuse
    
    What this does:
    1. Tracks request timestamps per IP address
    2. Removes old timestamps outside the time window
    3. Checks if current IP has exceeded request limit
    4. Adds current request timestamp to tracking
    
    Why rate limiting?:
    - Prevents spam/abuse of AI service
    - Protects against expensive API calls
    - Ensures fair usage across users
    - Prevents accidental infinite request loops
    
    Rate limit: 10 requests per minute per IP address
    
    Parameters:
        ip_address: Client IP address from request
    
    Returns:
        True if request allowed, False if rate limit exceeded
    """
    current_time = time.time()
    
    # Clean old entries outside the time window
    rate_limit_cache[ip_address] = [
        timestamp for timestamp in rate_limit_cache[ip_address]
        if current_time - timestamp < RATE_LIMIT_WINDOW
    ]
    
    # Check if rate limit exceeded
    if len(rate_limit_cache[ip_address]) >= RATE_LIMIT_REQUESTS:
        print(f"🚫 Rate limit exceeded for IP: {ip_address}")
        return False
    
    # Add current request timestamp
    rate_limit_cache[ip_address].append(current_time)
    return True

def get_cache_key(question, request_id=None):
    """
    Generate Unique Cache Key for Questions
    
    What this does:
    1. Normalizes question text (lowercase, trimmed)
    2. Optionally includes request ID for uniqueness
    3. Returns consistent key for caching system
    
    Why normalize?:
    - "What are your SKILLS?" and "what are your skills?" should use same cache
    - Improves cache hit rate and reduces duplicate AI calls
    
    Parameters:
        question: User's question text
        request_id: Optional unique request identifier
    
    Returns:
        String cache key for storing/retrieving responses
    """
    # Normalize question for consistent caching
    normalized_question = question.lower().strip()
    if request_id:
        return f"{normalized_question}_{request_id}"
    return normalized_question

def get_cached_response(cache_key):
    """
    Retrieve Cached Response if Available and Fresh
    
    What this does:
    1. Checks if response exists in cache
    2. Validates response is not expired (< 5 minutes old)
    3. Returns cached response or None if expired/missing
    
    Why cache responses?:
    - AI calls are expensive (time and cost)
    - Same questions often asked multiple times
    - Improves response speed for repeat questions
    
    Cache expiry: 5 minutes (prevents stale responses)
    
    Parameters:
        cache_key: Unique key for the cached response
    
    Returns:
        Cached response dict or None if not found/expired
    """
    if cache_key in request_cache:
        cached_time, cached_response = request_cache[cache_key]
        
        # Check if cache is still fresh (5 minutes = 300 seconds)
        if time.time() - cached_time < 300:
            print(f"📋 Cache hit for: {cache_key[:50]}...")
            return cached_response
        else:
            # Remove expired cache entry
            del request_cache[cache_key]
            print(f"🗑️ Expired cache removed for: {cache_key[:50]}...")
    
    return None

def cache_response(cache_key, response):
    """
    Store Response in Cache for Future Use
    
    What this does:
    1. Stores response with current timestamp
    2. Enables fast retrieval for duplicate questions
    3. Reduces load on AI services
    
    Cache format: {cache_key: (timestamp, response)}
    
    Parameters:
        cache_key: Unique key for the response
        response: Response dict to cache
    """
    request_cache[cache_key] = (time.time(), response)
    print(f"💾 Response cached for: {cache_key[:50]}...")

def get_rag_response(question: str) -> str:
    """
    Get AI Response Using RAG System with Fallback
    
    What this does:
    1. First tries full RAG system (Vector search + AI generation)
    2. Falls back to smart JSON search if RAG fails
    3. Returns natural language response
    
    Response Quality Hierarchy:
    1. RAG System (Best): AI-generated responses with context
    2. Smart Search (Good): Keyword matching in JSON data
    3. Fallback (Basic): Predefined responses
    
    This layered approach ensures the system always responds,
    even if some components fail.
    
    Parameters:
        question: User's question string
    
    Returns:
        Natural language response string
    """
    # Check if RAG system is available
    if not RAG_AVAILABLE:
        print("📋 RAG not available, using direct search")
        return smart_search_response(question)
    
    try:
        print(f"🤖 Processing RAG query: {question}")
        
        # Initialize RAG components
        groq_client, index = initialize_rag()
        
        # Verify initialization succeeded
        if not groq_client or not index:
            print("❌ RAG initialization failed, falling back")
            return smart_search_response(question)
        
        # Execute full RAG pipeline
        response = rag_query(index, groq_client, question)
        return response
        
    except Exception as e:
        print(f"❌ RAG system error: {e}")
        print("📋 Falling back to direct search")
        return smart_search_response(question)


def load_digitaltwin_data():
    """Load the detailed profile data from digitaltwin.json"""
    try:
        # Try to load from the same directory as this script
        script_dir = os.path.dirname(__file__)
        json_path = os.path.join(script_dir, 'digitaltwin.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading digitaltwin.json: {e}")
        return None

def smart_search_response(question: str) -> str:
    """Search through digitaltwin.json content for relevant answers"""
    data = load_digitaltwin_data()
    if not data:
        return get_fallback_response(question)
    
    question_lower = question.lower()
    content_chunks = data.get("content_chunks", [])
    
    # Find relevant content chunks based on question keywords
    relevant_chunks = []
    
    for chunk in content_chunks:
        title = chunk.get("title", "").lower()
        content = chunk.get("content", "").lower()
        category = chunk.get("metadata", {}).get("category", "").lower()
        tags = [tag.lower() for tag in chunk.get("metadata", {}).get("tags", [])]
        
        # Check if question matches this chunk
        if (any(keyword in title for keyword in question_lower.split()) or
            any(keyword in content for keyword in question_lower.split()) or
            any(keyword in category for keyword in question_lower.split()) or
            any(keyword in " ".join(tags) for keyword in question_lower.split())):
            
            relevant_chunks.append({
                "title": chunk.get("title", ""),
                "content": chunk.get("content", ""),
                "category": category,
                "relevance_score": calculate_relevance_score(question_lower, chunk)
            })
    
    # Sort by relevance and return best match
    if relevant_chunks:
        relevant_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
        best_match = relevant_chunks[0]
        return f"{best_match['content']}"
    
    return get_fallback_response(question)

def calculate_relevance_score(question: str, chunk: dict) -> int:
    """Calculate how relevant a chunk is to the question"""
    score = 0
    question_words = set(question.lower().split())
    
    title = chunk.get("title", "").lower()
    content = chunk.get("content", "").lower()
    category = chunk.get("metadata", {}).get("category", "").lower()
    tags = " ".join(chunk.get("metadata", {}).get("tags", [])).lower()
    
    # Score based on matches in different fields
    for word in question_words:
        if word in title: score += 10  # Title matches are most important
        if word in category: score += 8  # Category matches are very important
        if word in tags: score += 5     # Tag matches are important
        if word in content: score += 2  # Content matches are good
    
    return score

def get_fallback_response(question: str) -> str:
    """Enhanced fallback responses based on digitaltwin.json content"""
    
    # More comprehensive responses based on your actual profile
    fallback_responses = {
        "hello": "Hello! I'm Tsai Chun Lin. I'm a recent graduate with a Master of Applied Information Technology from Victoria University. I'm passionate about frontend and full-stack development. What would you like to know about my background?",
        
        "education": "I have a Master of Applied Information Technology from Victoria University (2024-2025) with a GPA of 6.25. My coursework included Advanced Web Development, Database Systems, Software Engineering, Cloud Computing, and Cybersecurity. I also have a Master of Information Systems & Advertising from University of Queensland (2021-2023) with a GPA of 5.37.",
        
        "experience": "I currently work part-time as a Barista at Kitchen Montague, which has helped me develop excellent customer service and time management skills. I also completed a Technical Support Internship at Ben Curtains (Jan 2025 - Apr 2025), where I organized website content, managed images via WordPress, and improved website loading speed by 30%.",
        
        "skills": "My technical skills include Python (2 years, beginner-intermediate), JavaScript (1 year, beginner-intermediate), and PHP (6 months, beginner). I'm proficient in HTML5, CSS3, Bootstrap for responsive design, and MySQL for database management. I use Git/GitHub for version control and I'm currently learning React.js and Node.js.",
        
        "projects": "My main project is Book 2 Drive - a driving lesson booking application where I led frontend development for a 3-person team. I designed responsive UI, implemented user authentication, and created MySQL database with proper ERD. The project received a High Distinction (85%) and supported 50+ test bookings. I've also built portfolio projects including responsive news homepages and multi-step forms.",
        
        "salary": "I'm looking for an entry to mid-level developer role with a salary range of $65,000 - $70,000 AUD annually. I'm open to Melbourne, Sydney, or Brisbane locations and willing to relocate within Australia. I'm available for hybrid work arrangements and can start immediately or with 2 weeks notice.",
        
        "goals": "My short-term goal is to secure a junior to mid-level frontend or full-stack developer position where I can gain commercial experience with React.js and Node.js. Long-term, I want to progress to senior developer or technical lead roles, contribute to architectural decisions, and potentially pursue team leadership opportunities.",
        
        "about": "I'm Tsai Chun Lin, passionate about creating engaging web applications and solving problems through code. I enjoy the creative problem-solving aspect of development and am motivated by technology's impact on user experience. I have strong foundations in multiple programming languages and proven ability to learn new technologies quickly."
    }
    
    question_lower = question.lower()
    
    # Check for greetings
    greetings = ["hello", "hi", "hey", "greetings", "how are you", "who are you"]
    if any(greeting in question_lower for greeting in greetings):
        return fallback_responses["hello"]
    
    # Check for specific topics with keyword matching
    topic_keywords = {
        "education": ["education", "university", "study", "degree", "gpa", "coursework", "graduate"],
        "experience": ["experience", "work", "job", "internship", "barista", "ben curtains", "kitchen montague"],
        "skills": ["skills", "programming", "languages", "python", "javascript", "php", "html", "css", "technical"],
        "projects": ["projects", "book 2 drive", "portfolio", "application", "website", "development"],
        "salary": ["salary", "pay", "money", "compensation", "range", "location", "melbourne", "sydney", "brisbane"],
        "goals": ["goals", "future", "career", "objectives", "plans", "ambitions"],
        "about": ["about", "background", "profile", "bio", "yourself", "tell me"]
    }
    
    # Find the best matching topic
    for topic, keywords in topic_keywords.items():
        if any(keyword in question_lower for keyword in keywords):
            return fallback_responses.get(topic, fallback_responses["about"])
    
    return "Thank you for your question! I'm Tsai Chun Lin, a frontend/full-stack developer. Feel free to ask me about my education, work experience, technical skills, projects like Book 2 Drive, career goals, or salary expectations. I'm always happy to discuss my background!"

class handler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler for Chat API
    
    This class handles incoming HTTP requests from the frontend chat interface.
    It processes GET requests to /api/chat and returns AI-generated responses.
    
    API Endpoint: GET /api/chat?question=<user_question>
    Response Format: {"answer": "...", "source": "...", "request_id": "..."}
    
    Features:
    - Rate limiting per IP address
    - Response caching for performance
    - CORS headers for browser compatibility  
    - Error handling with user-friendly messages
    """
    
    def do_GET(self):
        """
        Handle GET Requests to Chat API
        
        Request Flow:
        1. Extract client IP for rate limiting
        2. Check rate limits (10 requests/minute)
        3. Parse question from URL parameters
        4. Check cache for existing response
        5. Generate new response using RAG system
        6. Cache and return response
        
        Security Features:
        - Rate limiting prevents abuse
        - Input validation prevents errors
        - CORS headers enable browser requests
        """
        # Extract client IP address for rate limiting
        # X-Forwarded-For header used by proxies/load balancers
        client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
        
        # Apply rate limiting to prevent abuse
        if not check_rate_limit(client_ip):
            # Return 429 Too Many Requests status
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # User-friendly rate limit message
            response = {
                "error": "Rate limit exceeded",
                "answer": "Please wait a moment before sending another message. This helps me provide better responses."
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
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
            request_id = query_params.get('rid', [None])[0]  # Get request ID if provided
            
            if not question:
                response = {
                    "error": "Empty question",
                    "answer": "Please provide a valid question about my background, skills, or experience."
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Check for cached response
            cache_key = get_cache_key(question, request_id)
            cached_response = get_cached_response(cache_key)
            
            if cached_response:
                print(f"Returning cached response for: {question}")
                self.wfile.write(json.dumps(cached_response).encode())
                return
            
            # Get response using RAG system (with fallback to smart search)
            answer = get_rag_response(question)
            
            response = {
                "answer": answer,
                "source": "digital_twin_assistant",
                "request_id": request_id
            }
            
            # Cache the response
            cache_response(cache_key, response)
            
            print(f"Generated new response for: {question}")
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            print(f"Error processing request: {e}")
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