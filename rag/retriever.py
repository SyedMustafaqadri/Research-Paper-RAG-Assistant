from rag.vectorstore import get_vectorstore
from core.logger import logger

def retrieve_relevant_chunks(query: str, document_id: str = None, k: int = 5):
    """
    Retrieves the top-k relevant document chunks from ChromaDB for a given query.
    If document_id is provided, search is filtered to that specific document.
    """
    logger.info(f"Retrieving chunks for query: '{query}' (filter document_id: {document_id})")
    vectorstore = get_vectorstore()
    
    # Setup search filter if document_id is provided
    search_filter = None
    if document_id:
        search_filter = {"document_id": document_id}
        
    try:
        results = vectorstore.similarity_search(
            query,
            k=k,
            filter=search_filter
        )
        logger.info(f"Retrieved {len(results)} chunks.")
        return results
    except Exception as e:
        logger.error(f"Error during retrieval from ChromaDB: {e}")
        return []
