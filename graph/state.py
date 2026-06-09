from typing import TypedDict, List, Dict, Any
from langchain_core.documents import Document

class AgentState(TypedDict):
    """
    Defines the state of our LangGraph agent workflow.
    """
    question: str
    chat_history: List[Dict[str, str]]  # list of {"role": "...", "content": "..."}
    retrieved_docs: List[Document]
    answer: str
    sources: List[Dict[str, Any]]  # list of {"filename": "...", "page": ...}
    document_id: str  # Filter retrieval by specific document (optional)
