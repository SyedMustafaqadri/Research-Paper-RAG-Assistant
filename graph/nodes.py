from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.system_prompt import RAG_SYSTEM_PROMPT, SUMMARY_PROMPT
from rag.retriever import retrieve_relevant_chunks
from core.config import Config


def _extract_text(content) -> str:
    """
    Safely extract plain text from a LangChain response content.
    Newer langchain-google-genai versions may return a list of typed
    content blocks ({"type": "text", "text": "..."}) instead of a str.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

async def retrieve_node(state):
    """
    LangGraph node to retrieve relevant chunks from ChromaDB.
    """
    question = state["question"]
    doc_id = state.get("document_id")
    
    # Run retrieval
    retrieved = retrieve_relevant_chunks(question, document_id=doc_id, k=5)
    
    return {"retrieved_docs": retrieved}

async def generate_node(state):
    """
    LangGraph node to generate response using Gemini.
    """
    retrieved = state.get("retrieved_docs", [])
    question = state["question"]
    history = state.get("chat_history", [])
    
    # Format context
    context_str = ""
    for idx, doc in enumerate(retrieved):
        filename = doc.metadata.get("filename", "Unknown")
        page = doc.metadata.get("page", "?")
        context_str += f"\n--- Chunk {idx+1} from {filename} (Page {page}) ---\n{doc.page_content}\n"
        
    # Format history
    history_str = ""
    for msg in history:
        history_str += f"{msg['role'].capitalize()}: {msg['content']}\n"
        
    system_prompt = RAG_SYSTEM_PROMPT.format(context=context_str, history=history_str)
    
    # Initialize Gemini model
    model = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.0
    )
    
    response = await model.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ])
    
    # Extract sources
    sources = []
    seen_sources = set()
    for doc in retrieved:
        filename = doc.metadata.get("filename", "Unknown")
        page = doc.metadata.get("page", 1)
        source_key = (filename, page)
        if source_key not in seen_sources:
            seen_sources.add(source_key)
            sources.append({"filename": filename, "page": page})
            
    return {"answer": _extract_text(response.content), "sources": sources}

async def generate_summary(chunks, filename: str) -> str:
    """
    Utility helper to generate a structured summary from paper chunks.
    This does not run as part of the Q&A graph, but is a dedicated service call.
    """
    # Combine content up to limit to avoid hitting rate limits or tokens
    context_str = ""
    # Sort chunks to try summarizing in order
    sorted_chunks = sorted(chunks, key=lambda c: (c.get("page_number", 1), c.get("chunk_index", 0)))
    
    # Take up to top 15 chunks (about 15k characters) to give a good summary representation
    for idx, chunk in enumerate(sorted_chunks[:15]):
        page = chunk.get("page_number", 1)
        context_str += f"\n[Page {page}]\n{chunk.get('chunk_text', '')}\n"
        
    prompt = SUMMARY_PROMPT.format(context=context_str)
    
    model = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=Config.GOOGLE_API_KEY,
        temperature=0.2
    )
    
    response = await model.ainvoke([
        {"role": "user", "content": prompt}
    ])
    return _extract_text(response.content)
