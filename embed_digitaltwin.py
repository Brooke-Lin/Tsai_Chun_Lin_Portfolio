#!/usr/bin/env python3
"""
Digital Twin Embedding Script - Data Preparation for RAG System

Purpose: This script prepares your professional data for the AI chat system

What this script does:
1. Reads your professional information from digitaltwin.json
2. Converts text content into searchable vectors (embeddings)
3. Uploads vectors to Upstash Vector database
4. Tests the search functionality

Why Embeddings?:
- Embeddings convert text into mathematical vectors
- Similar concepts have similar vectors (semantic search)
- Example: "job" and "career" are close in vector space
- Enables AI to find relevant information based on meaning, not just keywords

When to run this script:
- First time setup: python embed_digitaltwin.py
- After updating your professional data in digitaltwin.json
- To reset/refresh your AI knowledge base

Process Flow:
JSON Data → Text Chunks → Vector Embeddings → Database Storage → Search Testing
"""

# Import required libraries
import os                    # For environment variables
import json                  # For parsing JSON data files
from dotenv import load_dotenv    # For loading .env file with API keys
from upstash_vector import Index  # Upstash vector database client

# Load environment variables from .env file
# This reads database URLs and tokens securely
load_dotenv()

# Configuration Constants
JSON_FILE = "digitaltwin.json"                           # Your professional data file
UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')      # Database URL
UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')  # Database access token

def setup_vector_database():
    """
    Establish Connection to Upstash Vector Database
    
    What this does:
    1. Validates database credentials from .env file
    2. Creates connection to Upstash Vector cloud service
    3. Returns database index object for operations
    
    Upstash Vector is a cloud vector database that:
    - Stores text as mathematical vectors (embeddings)
    - Provides fast similarity search
    - Has built-in embedding generation
    - Requires no local setup or maintenance
    
    Credentials needed in .env file:
    - UPSTASH_VECTOR_REST_URL: Your database endpoint
    - UPSTASH_VECTOR_REST_TOKEN: Authentication token
    
    Returns:
        Database index object or None if connection fails
    """
    print("🔄 Setting up Upstash Vector database...")
    
    # Validate that required environment variables exist
    if not UPSTASH_VECTOR_REST_URL or not UPSTASH_VECTOR_REST_TOKEN:
        print("❌ UPSTASH_VECTOR_REST_URL or UPSTASH_VECTOR_REST_TOKEN not found in .env file")
        print("💡 Please check your .env file has the correct Upstash credentials")
        return None
    
    try:
        # Create database connection using credentials
        index = Index(
            url=UPSTASH_VECTOR_REST_URL,      # Database endpoint URL
            token=UPSTASH_VECTOR_REST_TOKEN   # Authentication token
        )
        print("✅ Connected to Upstash Vector successfully!")
        return index
    except Exception as e:
        print(f"❌ Error connecting to Upstash Vector: {str(e)}")
        print("💡 Check if your Upstash credentials are correct")
        return None

def load_digital_twin_data():
    """
    Load Your Professional Data from JSON File
    
    What this does:
    1. Opens and reads digitaltwin.json file
    2. Parses JSON structure containing your professional information
    3. Returns structured data for processing
    
    digitaltwin.json structure:
    {
        "personal": {...},           // Basic info, contact details
        "experience": [...],         // Work history
        "education": [...],          // Academic background  
        "content_chunks": [...]      // Searchable content pieces
    }
    
    The content_chunks section is most important for AI:
    - Contains bite-sized pieces of your professional info
    - Each chunk has title, content, metadata, and tags
    - These chunks become searchable vectors in the database
    
    Returns:
        Parsed JSON data dictionary or None if file not found
    """
    try:
        # Open and read JSON file with UTF-8 encoding (supports special characters)
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Parse JSON into Python dictionary
        print(f"✅ Loaded digital twin data from {JSON_FILE}")
        return data
    except FileNotFoundError:
        print(f"❌ {JSON_FILE} not found! Please create the file first.")
        print("💡 Make sure digitaltwin.json exists in the current directory")
        return None
    except Exception as e:
        print(f"❌ Error loading {JSON_FILE}: {str(e)}")
        print("💡 Check if the JSON file is properly formatted")
        return None

def prepare_vectors_from_content_chunks(digital_twin_data):
    """
    Convert Professional Data into Vector Format
    
    What this does:
    1. Extracts content_chunks from your professional data
    2. Combines title and content for better search context
    3. Packages each chunk into vector format for database upload
    4. Preserves metadata for filtering and context
    
    Vector Format Explained:
    Each vector is a tuple: (id, text_to_embed, metadata)
    - id: Unique identifier for the content piece
    - text_to_embed: The actual text that becomes a vector
    - metadata: Additional info stored with the vector
    
    Why Combine Title + Content?:
    "Education: I have a Master's degree..." is more searchable than just the content
    This gives the AI better context when matching user questions
    
    Example transformation:
    Input chunk: {"id": "edu1", "title": "Education", "content": "Master's degree..."}
    Output vector: ("edu1", "Education: Master's degree...", {metadata})
    
    Parameters:
        digital_twin_data: Loaded JSON data from digitaltwin.json
    
    Returns:
        List of vector tuples ready for database upload
    """
    # Extract content chunks from the loaded data
    content_chunks = digital_twin_data.get('content_chunks', [])
    
    if not content_chunks:
        print("❌ No content_chunks found in digital twin data")
        print("💡 Make sure your digitaltwin.json has a 'content_chunks' section")
        return []
    
    vectors = []
    
    # Process each content chunk
    for chunk in content_chunks:
        # Create enriched text by combining title and content
        # This gives better search context than content alone
        enriched_text = f"{chunk['title']}: {chunk['content']}"
        
        # Create vector tuple in format expected by Upstash Vector
        vector = (
            chunk['id'],          # Unique identifier
            enriched_text,        # Text that will be converted to embedding
            {                     # Metadata stored alongside the vector
                "title": chunk['title'],
                "type": chunk['type'], 
                "content": chunk['content'],
                "category": chunk.get('metadata', {}).get('category', ''),
                "tags": chunk.get('metadata', {}).get('tags', [])
            }
        )
        vectors.append(vector)
    
    print(f"✅ Prepared {len(vectors)} vectors from content chunks")
    return vectors

def clear_existing_vectors(index):
    """Clear existing vectors from the database"""
    try:
        # Get current vector count
        info = index.info()
        current_count = getattr(info, 'vector_count', 0)
        
        if current_count > 0:
            print(f"🗑️ Found {current_count} existing vectors. Clearing database...")
            
            # Reset the index (this clears all vectors)
            index.reset()
            print("✅ Existing vectors cleared successfully")
        else:
            print("📝 No existing vectors found. Database is clean.")
            
    except Exception as e:
        print(f"⚠️ Warning: Could not clear existing vectors: {str(e)}")
        print("Proceeding with upsert (existing vectors will be updated)")

def upload_vectors_to_database(index, vectors):
    """Upload vectors to Upstash Vector database"""
    try:
        print(f"🚀 Uploading {len(vectors)} vectors to Upstash Vector...")
        
        # Upload in batches for better reliability
        batch_size = 50
        total_vectors = len(vectors)
        
        for i in range(0, total_vectors, batch_size):
            batch = vectors[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_vectors + batch_size - 1) // batch_size
            
            print(f"📦 Uploading batch {batch_num}/{total_batches} ({len(batch)} vectors)...")
            
            index.upsert(vectors=batch)
            
        print("✅ All vectors uploaded successfully!")
        
        # Verify upload
        try:
            info = index.info()
            final_count = getattr(info, 'vector_count', 0)
            print(f"📊 Final vector count in database: {final_count}")
        except:
            print("📊 Upload completed (could not verify final count)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error uploading vectors: {str(e)}")
        return False

def test_vector_search(index):
    """Test the vector search functionality"""
    print("\n🧪 Testing vector search functionality...")
    
    test_queries = [
        "What are your technical skills?",
        "Tell me about your education background", 
        "Describe your work experience",
        "What projects have you worked on?"
    ]
    
    for query in test_queries:
        try:
            print(f"\n🔍 Testing query: '{query}'")
            results = index.query(
                data=query,
                top_k=2,
                include_metadata=True
            )
            
            if results:
                for i, result in enumerate(results):
                    metadata = result.metadata or {}
                    title = metadata.get('title', 'Unknown')
                    score = result.score
                    print(f"  {i+1}. {title} (score: {score:.3f})")
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Error testing query: {str(e)}")
    
    print("\n✅ Vector search testing completed!")

def main():
    """Main embedding process"""
    print("🤖 Digital Twin Embedding Script")
    print("=" * 50)
    print("📋 Processing digitaltwin.json for RAG system")
    print("🔗 Vector Storage: Upstash (built-in embeddings)")
    print()
    
    # Step 1: Setup database connection
    index = setup_vector_database()
    if not index:
        print("❌ Failed to connect to vector database. Exiting.")
        return False
    
    # Step 2: Load digital twin data
    digital_twin_data = load_digital_twin_data()
    if not digital_twin_data:
        print("❌ Failed to load digital twin data. Exiting.")
        return False
    
    # Step 3: Prepare vectors from content chunks
    vectors = prepare_vectors_from_content_chunks(digital_twin_data)
    if not vectors:
        print("❌ Failed to prepare vectors. Exiting.")
        return False
    
    # Step 4: Clear existing vectors (optional - comment out to keep existing data)
    clear_existing_vectors(index)
    
    # Step 5: Upload vectors to database
    success = upload_vectors_to_database(index, vectors)
    if not success:
        print("❌ Failed to upload vectors. Exiting.")
        return False
    
    # Step 6: Test the vector search
    test_vector_search(index)
    
    print("\n🎉 Digital twin embedding completed successfully!")
    print("Your RAG system is now ready to answer questions about your professional profile.")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your environment configuration and try again.")