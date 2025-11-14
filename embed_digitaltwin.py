#!/usr/bin/env python3
"""
Digital Twin Embedding Script
Processes digitaltwin.json content chunks and uploads to Upstash Vector database
Based on the course requirements for structured RAG data
"""

import os
import json
from dotenv import load_dotenv
from upstash_vector import Index

# Load environment variables
load_dotenv()

# Constants
JSON_FILE = "digitaltwin.json"
UPSTASH_VECTOR_REST_URL = os.getenv('UPSTASH_VECTOR_REST_URL')
UPSTASH_VECTOR_REST_TOKEN = os.getenv('UPSTASH_VECTOR_REST_TOKEN')

def setup_vector_database():
    """Setup Upstash Vector database connection"""
    print("🔄 Setting up Upstash Vector database...")
    
    if not UPSTASH_VECTOR_REST_URL or not UPSTASH_VECTOR_REST_TOKEN:
        print("❌ UPSTASH_VECTOR_REST_URL or UPSTASH_VECTOR_REST_TOKEN not found in .env file")
        return None
    
    try:
        index = Index(
            url=UPSTASH_VECTOR_REST_URL,
            token=UPSTASH_VECTOR_REST_TOKEN
        )
        print("✅ Connected to Upstash Vector successfully!")
        return index
    except Exception as e:
        print(f"❌ Error connecting to Upstash Vector: {str(e)}")
        return None

def load_digital_twin_data():
    """Load digital twin data from JSON file"""
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded digital twin data from {JSON_FILE}")
        return data
    except FileNotFoundError:
        print(f"❌ {JSON_FILE} not found! Please create the file first.")
        return None
    except Exception as e:
        print(f"❌ Error loading {JSON_FILE}: {str(e)}")
        return None

def prepare_vectors_from_content_chunks(digital_twin_data):
    """Prepare vectors from content chunks in the digital twin data"""
    content_chunks = digital_twin_data.get('content_chunks', [])
    
    if not content_chunks:
        print("❌ No content_chunks found in digital twin data")
        return []
    
    vectors = []
    
    for chunk in content_chunks:
        # Create enriched text for embedding
        enriched_text = f"{chunk['title']}: {chunk['content']}"
        
        # Prepare vector with metadata
        vector = (
            chunk['id'],  # ID
            enriched_text,  # Text to embed
            {
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