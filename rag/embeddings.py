from langchain_google_genai import GoogleGenerativeAIEmbeddings 
from core.config import Config

def get_embeddings():
    """Returns the Google GenAI Embeddings instance."""
    # Ensure Config is validated when running the actual RAG pipeline
    Config.validate()
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview",
        google_api_key=Config.GOOGLE_API_KEY
    )
