from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from digitaltwin_rg import rag_query, setup_groq_client, setup_vector_database

app = FastAPI()

# Allow requests from your website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your URL when live
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Groq client and vector database once
groq_client = setup_groq_client()
index = setup_vector_database()

@app.get("/ask")
def ask(question: str):
    if not question:
        return {"answer": "Please provide a question."}
    answer = rag_query(index, groq_client, question)
    return {"answer": answer}
