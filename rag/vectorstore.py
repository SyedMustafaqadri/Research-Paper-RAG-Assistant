from langchain_chroma import Chroma
from rag.embeddings import get_embeddings
from core.config import Config

def get_vectorstore(collection_name="research_papers"):
    """Returns the persistent Chroma vector store."""
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=Config.CHROMA_DB_PATH_ABS,
        embedding_function=embeddings,
        collection_name=collection_name
    )
