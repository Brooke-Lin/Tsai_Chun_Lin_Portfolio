"""
Digital Twin RAG (Retrieval-Augmented Generation) Application

This file implements the core RAG system for the AI chat box:
1. RAG = Retrieval-Augmented Generation (AI technique that combines search + LLM)
2. Upstash Vector: Cloud vector database with built-in text embeddings
3. Groq: Ultra-fast Large Language Model (LLM) inference service
4. Process: User question → Search relevant info → Generate AI response

Architecture Flow:
Question → Vector Search → Context Retrieval → LLM Generation → Response

Technologies:
- Upstash Vector: Stores and searches your professional data as vectors
- Groq LLM: Generates human-like responses using Llama-3.1-8b-instant model
- Python dotenv: Manages API keys and environment variables securely
"""

# Import required libraries
import os                    # For operating system environment variables
import json                  # For parsing JSON data files
from dotenv import load_dotenv    # For loading .env file with API keys
from upstash_vector import Index  # Upstash vector database client
from groq import Groq            # Groq AI client for LLM inference

# Load environment variables from .env file
# This reads API keys and database URLs from the .env file for security
load_dotenv()

# Configuration Constants
JSON_FILE = "digitaltwin.json"                    # Your professional data file
GROQ_API_KEY = os.getenv('GROQ_API_KEY')         # API key for Groq LLM service
DEFAULT_MODEL = "llama-3.1-8b-instant"          # Fast, efficient Groq LLM model

def setup_groq_client():
    """
    Initialize Groq AI Client for Large Language Model (LLM) Inference
    
    What this does:
    1. Checks if API key exists in environment variables
    2. Creates a connection to Groq's AI service
    3. Returns client object for making AI requests
    
    Groq is an AI inference company that provides ultra-fast LLM processing
    using specialized hardware (LPU - Language Processing Units)
    
    Returns:
        Groq client object or None if setup fails
    """
    # Check if API key exists (loaded from .env file)
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not found in .env file")
        print("💡 Please add GROQ_API_KEY=your_key_here to .env file")
        return None
    
    try:
        # Initialize Groq client with API key
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client initialized successfully!")
        return client
    except Exception as e:
        print(f"❌ Error initializing Groq client: {str(e)}")
        print("💡 Check if your GROQ_API_KEY is valid")
        return None

def setup_vector_database():
    """
    Initialize Upstash Vector Database for Semantic Search
    
    What is a Vector Database?:
    - Stores text as mathematical vectors (embeddings)
    - Enables semantic similarity search (meaning-based, not just keyword matching)
    - Example: "job" and "career" are similar even if different words
    
    Process:
    1. Connect to Upstash Vector (cloud vector database)
    2. Check if database already has your profile data
    3. If empty, load and upload your professional information
    4. Convert text to vectors using built-in embeddings
    
    Upstash Vector Features:
    - Built-in embeddings (automatically converts text to vectors)
    - Cloud-hosted (no local setup needed)
    - Fast similarity search
    
    Returns:
        Vector database index object or None if setup fails
    """
    print("🔄 Setting up Upstash Vector database...")
    
    try:
        # Connect to Upstash Vector using environment variables from .env file
        # Index.from_env() automatically reads UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN
        index = Index.from_env()
        print("✅ Connected to Upstash Vector successfully!")
        
        # Check current vector count to see if database is already populated
        try:
            info = index.info()  # Get database information
            current_count = getattr(info, 'vector_count', 0)  # Get number of stored vectors
            print(f"📊 Current vectors in database: {current_count}")
        except:
            # If info() fails, assume database is empty
            current_count = 0
        
        # Load and upload data if database is empty (first time setup)
        if current_count == 0:
            print("📝 Loading your professional profile...")
            
            # Load your professional data from JSON file
            try:
                with open(JSON_FILE, "r", encoding="utf-8") as f:
                    profile_data = json.load(f)
            except FileNotFoundError:
                print(f"❌ {JSON_FILE} not found!")
                print("💡 Please run: python embed_digitaltwin.py first")
                return None
            
            # Prepare vectors from content chunks
            vectors = []
            content_chunks = profile_data.get('content_chunks', [])
            
            if not content_chunks:
                print("❌ No content chunks found in profile data")
                print("💡 Please check your digitaltwin.json structure")
                return None
            
            # Convert each content chunk to a vector
            for chunk in content_chunks:
                # Create enriched text by combining title and content
                # This gives better search context
                enriched_text = f"{chunk['title']}: {chunk['content']}"
                
                # Create vector tuple: (id, text_to_embed, metadata)
                vectors.append((
                    chunk['id'],           # Unique identifier
                    enriched_text,         # Text that will be converted to vector
                    {                      # Metadata for filtering and context
                        "title": chunk['title'],
                        "type": chunk['type'],
                        "content": chunk['content'],
                        "category": chunk.get('metadata', {}).get('category', ''),
                        "tags": chunk.get('metadata', {}).get('tags', [])
                    }
                ))
            
            # Upload vectors to database
            # Upstash will automatically create embeddings from the text
            index.upsert(vectors=vectors)
            print(f"✅ Successfully uploaded {len(vectors)} content chunks!")
        
        return index
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        print("💡 Check your UPSTASH_VECTOR credentials in .env file")
        return None

def query_vectors(index, query_text, top_k=3):
    """
    Search Vector Database for Relevant Information
    
    What this does:
    1. Takes user's question as input
    2. Converts question to vector using embeddings
    3. Finds most similar vectors in database
    4. Returns top matches with similarity scores
    
    How Vector Search Works:
    - Your question: "What are your skills?"
    - Database has: vectors for education, experience, skills, projects
    - System finds vectors most similar to your question
    - Returns: Skills section, relevant project info, etc.
    
    Parameters:
        index: Vector database connection
        query_text: User's question
        top_k: Number of results to return (default: 3)
    
    Returns:
        List of similar vectors with metadata and similarity scores
    """
    try:
        # Perform similarity search in vector database
        results = index.query(
            data=query_text,           # User's question (will be converted to vector)
            top_k=top_k,              # Return top 3 most similar results
            include_metadata=True      # Include stored metadata (title, content, etc.)
        )
        return results
    except Exception as e:
        print(f"❌ Error querying vectors: {str(e)}")
        return None

def generate_response_with_groq(client, prompt, model=DEFAULT_MODEL):
    """
    Generate AI Response Using Groq Large Language Model (LLM)
    
    What this does:
    1. Takes context and user question as input
    2. Sends to Groq's LLM (Llama-3.1-8b-instant)
    3. Gets back human-like response in your voice
    4. Returns natural language answer
    
    How LLMs Work:
    - Large Language Models are AI trained on massive text data
    - They understand context and generate human-like text
    - Groq uses specialized hardware (LPUs) for ultra-fast inference
    
    Chat Completion Format:
    - System message: Sets AI personality and behavior
    - User message: Contains context + question
    - AI generates response as if it's you speaking
    
    Parameters:
        client: Groq AI client connection
        prompt: Context + question for AI
        model: Which AI model to use (default: llama-3.1-8b-instant)
    
    Returns:
        Generated response text or error message
    """
    try:
        # Create chat completion request to Groq AI
        completion = client.chat.completions.create(
            model=model,              # AI model to use (fast Llama variant)
            messages=[
                {
                    "role": "system",
                    # System prompt defines AI personality and behavior
                    "content": "You are an AI digital twin representing Tsai Chun Lin. Answer questions as if you are Tsai, speaking in first person about your background, skills, and experience. Be confident, professional, and specific about your achievements."
                },
                {
                    "role": "user",
                    # User prompt contains context from vector search + question
                    "content": prompt
                }
            ],
            temperature=0.7,          # Controls creativity (0.0 = predictable, 1.0 = creative)
            max_tokens=500           # Maximum response length
        )
        
        # Extract and return the generated text
        return completion.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ Error generating response: {str(e)}"

def rag_query(index, groq_client, question):
    """
    Main RAG (Retrieval-Augmented Generation) Function
    
    This is the core function that combines vector search + AI generation:
    
    RAG Process Explained:
    1. RETRIEVAL: Search your professional data for relevant information
    2. AUGMENTATION: Combine found information with user's question
    3. GENERATION: Use AI to create natural response in your voice
    
    Why RAG is Powerful:
    - AI alone doesn't know your specific background
    - Search alone doesn't generate natural responses
    - RAG combines both: finds YOUR data + generates natural answers
    
    Real Example:
    Question: "What are your programming skills?"
    → Search finds: Skills section, relevant projects
    → AI generates: "I have 5 years of Python experience and have built projects like..."
    
    Parameters:
        index: Vector database connection
        groq_client: AI client connection  
        question: User's question
    
    Returns:
        Natural language response about your professional background
    """
    try:
        # Step 1: RETRIEVAL - Query vector database for relevant information
        print("🔍 Step 1: Searching your professional data...")
        results = query_vectors(index, question, top_k=3)
        
        # Check if any relevant information was found
        if not results or len(results) == 0:
            return "I don't have specific information about that topic in my professional profile."
        
        # Step 2: AUGMENTATION - Extract and prepare relevant content
        print("🧠 Step 2: Extracting relevant information...")
        
        top_docs = []  # Will store the most relevant content
        for result in results:
            metadata = result.metadata or {}  # Get stored metadata
            title = metadata.get('title', 'Information')
            content = metadata.get('content', '')
            score = result.score  # Similarity score (higher = more relevant)
            
            print(f"🔹 Found: {title} (Relevance: {score:.3f})")
            if content:
                # Format content for AI prompt
                top_docs.append(f"{title}: {content}")
        
        if not top_docs:
            return "I found some information but couldn't extract details."
        
        # Step 3: GENERATION - Create AI prompt and generate response
        print(f"⚡ Step 3: Generating personalized response...")
        
        # Combine all relevant content into context
        context = "\n\n".join(top_docs)
        
        # Create structured prompt for AI
        prompt = f"""Based on the following information about yourself, answer the question.
Speak in first person as if you are describing your own background.

Your Information:
{context}

Question: {question}

Provide a helpful, professional response:"""
        
        # Generate final response using AI
        response = generate_response_with_groq(groq_client, prompt)
        return response
    
    except Exception as e:
        return f"❌ Error during RAG query: {str(e)}"

def main():
    """
    Main Application Entry Point - Interactive Digital Twin Chat
    
    What this does:
    1. Initializes all systems (AI client, vector database)
    2. Provides interactive command-line chat interface
    3. Processes questions using full RAG pipeline
    4. Allows testing of the digital twin system
    
    This function demonstrates the complete RAG workflow:
    - User asks question
    - System searches your professional data
    - AI generates personalized response
    - User gets natural language answer
    
    Usage:
    Run: python digitaltwin_rag.py
    Then type questions about your professional background
    """
    # Display system information
    print("🤖 Your Digital Twin - AI Profile Assistant")
    print("=" * 50)
    print("🔗 Vector Storage: Upstash (built-in embeddings)")
    print(f"⚡ AI Inference: Groq ({DEFAULT_MODEL})")
    print("📋 Data Source: Your Professional Profile\n")
    
    # Step 1: Initialize AI client
    print("Initializing AI systems...")
    groq_client = setup_groq_client()
    if not groq_client:
        print("❌ Failed to initialize AI client. Exiting.")
        return
    
    # Step 2: Initialize vector database
    index = setup_vector_database()
    if not index:
        print("❌ Failed to initialize vector database. Exiting.")
        return
    
    print("✅ Your Digital Twin is ready!\n")
    
    # Step 3: Interactive chat loop
    print("🤖 Chat with your AI Digital Twin!")
    print("Ask questions about your experience, skills, projects, or career goals.")
    print("Type 'exit' to quit.\n")
    
    # Provide example questions to help users get started
    print("💭 Try asking:")
    print("  - 'Tell me about your work experience'")
    print("  - 'What are your technical skills?'")
    print("  - 'Describe your career goals'")
    print("  - 'What projects have you worked on?'")
    print("  - 'What is your education background?'")
    print("  - 'What are your salary expectations?'")
    print()
    
    # Main chat loop
    while True:
        # Get user input
        question = input("You: ")
        
        # Check for exit commands
        if question.lower() in ["exit", "quit"]:
            print("👋 Thanks for chatting with your Digital Twin!")
            break
        
        # Process non-empty questions
        if question.strip():
            # Run complete RAG pipeline
            answer = rag_query(index, groq_client, question)
            print(f"🤖 Digital Twin: {answer}\n")

# Entry point - runs when file is executed directly
if __name__ == "__main__":
    """
    This block runs when you execute: python digitaltwin_rag.py
    It starts the interactive chat session with your digital twin
    """
    main()