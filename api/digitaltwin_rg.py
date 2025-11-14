import os
import json
from dotenv import load_dotenv
from upstash_vector import Index
from groq import Groq

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "digitaltwin.json"
PORTFOLIO_QA_FILE = "../portfolio-info.json"  # New Q&A format
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = "llama-3.1-8b-instant"

def setup_groq_client():
    """Setup Groq client"""
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env file")
        return None
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized successfully!")
        return client
    except Exception as e:
        print(f"❌ Error initializing Groq client: {str(e)}")
        return None

def load_portfolio_qa():
    """Load the portfolio Q&A format from portfolio-info.json"""
    try:
        script_dir = os.path.dirname(__file__)
        qa_path = os.path.join(script_dir, PORTFOLIO_QA_FILE)
        
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_data = json.load(f)
        print(f"✅ Loaded {len(qa_data)} Q&A pairs from portfolio-info.json")
        return qa_data
    except FileNotFoundError:
        print(f"❌ {PORTFOLIO_QA_FILE} not found! Falling back to digitaltwin.json")
        return None
    except Exception as e:
        print(f"❌ Error loading portfolio Q&A: {str(e)}")
        return None

def setup_vector_database():
    """Setup Upstash Vector database with built-in embeddings"""
    print("🔄 Setting up Upstash Vector database...")
    try:
        index = Index.from_env()
        print("✅ Connected to Upstash Vector successfully!")
        
        # Check current vector count
        try:
            info = index.info()
            current_count = getattr(info, "vector_count", 0)
            print(f"📊 Current vectors in database: {current_count}")
        except:
            current_count = 0
        
        # Load data if database is empty
        if current_count == 0:
            print("📝 Loading your professional profile...")
            
            # Try to load Q&A format first
            qa_data = load_portfolio_qa()
            
            if qa_data:
                # Use new Q&A format
                vectors = []
                for i, item in enumerate(qa_data):
                    # Combine question and answer for better context
                    combined_text = f"Question: {item['question']} Answer: {item['answer']}"
                    
                    vectors.append((
                        f"qa_{i}",  # Unique ID
                        combined_text,
                        {
                            "question": item['question'],
                            "answer": item['answer'],
                            "text": combined_text,
                            "type": "qa_pair"
                        }
                    ))
                
                # Upload vectors
                index.upsert(vectors=vectors)
                print(f"✅ Successfully uploaded {len(vectors)} Q&A pairs!")
                
            else:
                # Fallback to old format
                try:
                    with open(JSON_FILE, "r", encoding="utf-8") as f:
                        profile_data = json.load(f)
                except FileNotFoundError:
                    print(f"❌ {JSON_FILE} not found!")
                    return None
                
                # Prepare vectors from content chunks
                vectors = []
                content_chunks = profile_data.get("content_chunks", [])
                
                if not content_chunks:
                    print("❌ No content chunks found in profile data")
                    return None
                
                for chunk in content_chunks:
                    enriched_text = f"{chunk['title']}: {chunk['content']}"
                    vectors.append((
                        chunk["id"],
                        enriched_text,
                        {
                            "title": chunk["title"],
                            "type": chunk["type"],
                            "content": chunk["content"],
                            "category": chunk.get("metadata", {}).get("category", ""),
                            "tags": chunk.get("metadata", {}).get("tags", [])
                        }
                    ))
                
                # Upload vectors
                index.upsert(vectors=vectors)
                print(f"✅ Successfully uploaded {len(vectors)} content chunks!")
        
        return index
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        return None

def query_vectors(index, query_text, top_k=3):
    """Query Upstash Vector for similar vectors"""
    try:
        results = index.query(
            data=query_text,
            top_k=top_k,
            include_metadata=True
        )
        return results
    except Exception as e:
        print(f"❌ Error querying vectors: {str(e)}")
        return None

def generate_response_with_groq(client, prompt, model=DEFAULT_MODEL):
    """Generate response using Groq"""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are Tsai Chun Lin, a friendly and professional recent graduate. "
                        "Speak naturally as yourself, using 'I' statements. Be conversational but professional, "
                        "enthusiastic about technology, and helpful when discussing your background. "
                        "Avoid being robotic - respond like a real person having a friendly conversation."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

def is_inappropriate_question(question):
    """Check if a question is too personal or inappropriate for a professional context"""
    question_lower = question.lower().strip()
    
    # Personal/private topics
    personal_keywords = [
        'age', 'old', 'birthday', 'birth', 'year born',
        'gender', 'sex', 'male', 'female', 'man', 'woman',
        'married', 'single', 'relationship', 'dating', 'boyfriend', 'girlfriend',
        'religion', 'political', 'politics', 'vote',
        'address', 'home', 'where live', 'personal phone', 'weight', 'height'
    ]
    
    # Check if question contains personal keywords
    for keyword in personal_keywords:
        if keyword in question_lower:
            return True, keyword
    
    return False, None

def generate_polite_decline(question, detected_keyword):
    """Generate a polite response for inappropriate questions"""
    responses = {
        'age': "I prefer to keep my age private, but I'm a recent graduate ready to start my career! What I can tell you is about my recent education and technical skills.",
        'gender': "I'd rather focus on my professional qualifications and technical skills. Is there something specific about my experience you'd like to know?",
        'personal': "That's quite personal! I'd love to talk about my professional background instead. What aspects of my technical skills or projects interest you?",
        'default': "I prefer to keep that information private. Let me tell you about my professional background instead - what would you like to know about my skills or experience?"
    }
    
    if 'age' in detected_keyword or 'old' in detected_keyword or 'birth' in detected_keyword:
        return responses['age']
    elif 'gender' in detected_keyword or 'sex' in detected_keyword:
        return responses['gender']
    else:
        return responses['default']

def rag_query(index, groq_client, question):
    """Perform RAG query using Upstash Vector + Groq with smart question handling"""
    try:
        # Step 0: Check if question is inappropriate
        is_inappropriate, detected_keyword = is_inappropriate_question(question)
        if is_inappropriate:
            return generate_polite_decline(question, detected_keyword)
        
        # Step 1: Query vector database
        results = query_vectors(index, question, top_k=3)
        
        # Check relevance threshold - if no good matches, provide intelligent fallback
        best_score = results[0].score if results and len(results) > 0 else 0
        
        if not results or len(results) == 0 or best_score < 0.5:
            return handle_out_of_scope_question(groq_client, question)
        
        # Step 2: Extract relevant content
        print("🧠 Searching your professional profile...")
        top_docs = []
        for result in results:
            metadata = result.metadata or {}
            score = result.score
            
            # Only include results with decent relevance scores
            if score < 0.3:
                continue
                
            # Check if this is Q&A format or old content chunk format
            if metadata.get("type") == "qa_pair":
                # New Q&A format
                question_text = metadata.get("question", "")
                answer_text = metadata.get("answer", "")
                print(f"🔹 Found Q&A: {question_text[:50]}... (Relevance: {score:.3f})")
                if answer_text:
                    top_docs.append(f"Q: {question_text}\nA: {answer_text}")
            else:
                # Old content chunk format
                title = metadata.get("title", "Information")
                content = metadata.get("content", "")
                print(f"🔹 Found: {title} (Relevance: {score:.3f})")
                if content:
                    top_docs.append(f"{title}: {content}")
        
        if not top_docs:
            return handle_out_of_scope_question(groq_client, question)
        
        print("⚡ Generating personalized response...")
        context = "\n\n".join(top_docs)
        
        # Enhanced prompt for more natural conversation
        prompt = f"""You are Tsai Chun Lin, responding as yourself in a natural, conversational way. 
You're speaking to someone who's interested in your professional background.

Key personality traits:
- Professional but friendly and approachable
- Enthusiastic about technology and learning
- Confident but humble about your skills
- Natural conversational style (not robotic)

Based on this information about yourself, answer the question naturally as if you're having a friendly conversation:

{context}

Question: {question}

Respond naturally as Tsai Chun Lin would, using "I" statements. Keep it conversational but professional:"""
        
        response = generate_response_with_groq(groq_client, prompt)
        return response
    
    except Exception as e:
        return f"❌ Error during query: {str(e)}"

def handle_out_of_scope_question(groq_client, question):
    """Handle questions that don't have good matches in the knowledge base"""
    
    # Create a response that redirects to available information
    prompt = f"""You are Tsai Chun Lin responding to a question that's not directly covered in your portfolio information.
Respond naturally and conversationally, acknowledging the question but redirecting to what you can share about your professional background.

Question asked: {question}

Respond as yourself, being helpful while directing the conversation toward your:
- Education (Master's degrees from Victoria University and University of Queensland)
- Technical skills (Python, JavaScript, PHP, web development)
- Projects (Book 2 Drive, portfolio projects)
- Work experience (Technical Support Intern, Barista)
- Career goals (Frontend/Full-stack developer)

Keep it friendly and natural, like you're speaking to someone interested in your professional background:"""

    try:
        response = generate_response_with_groq(groq_client, prompt)
        return response
    except Exception as e:
        # Fallback response if AI generation fails
        return "That's an interesting question! While I don't have specific information about that, I'd be happy to tell you about my technical background, recent projects, or career goals. What aspects of my professional experience would you like to know more about?"

def main():
    """Main application loop"""
    print("🤖 Your Digital Twin - AI Profile Assistant")
    print("=" * 50)
    print("🔗 Vector Storage: Upstash (built-in embeddings)")
    print(f"⚡ AI Inference: Groq ({DEFAULT_MODEL})")
    print("📋 Data Source: Your Professional Profile\n")
    
    # Setup clients
    groq_client = setup_groq_client()
    if not groq_client:
        return
    
    index = setup_vector_database()
    if not index:
        return
    
    print("✅ Your Digital Twin is ready!\n")
    
    # Interactive chat loop
    print("🤖 Chat with your AI Digital Twin!")
    print("Ask questions about your experience, skills, projects, or career goals.")
    print("Type 'exit' to quit.\n")
    print("💭 Try asking:")
    print("  - 'Tell me about your work experience'")
    print("  - 'What are your technical skills?'")
    print("  - 'Describe your career goals'\n")
    
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("👋 Thanks for chatting with your Digital Twin!")
            break
        
        if question.strip():
            answer = rag_query(index, groq_client, question)
            print(f"🤖 Digital Twin: {answer}\n")

if __name__ == "__main__":
    main()
