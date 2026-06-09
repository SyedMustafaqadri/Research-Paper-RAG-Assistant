import uuid
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.logger import logger
from database.connection import get_db
from database.models import Document as DBDocument, DocumentChunk as DBDocumentChunk, User
from rag.vectorstore import get_vectorstore

def get_or_create_default_user(db):
    """Ensures a default user exists in the database."""
    user = db.query(User).filter_by(email="default@example.com").first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email="default@example.com",
            name="Default User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def ingest_pdf(file_path: str, filename: str) -> str:
    """
    Ingests a PDF file:
    1. Extracts text from PDF pages using pypdf.
    2. Splits text into chunks.
    3. Adds chunks to ChromaDB vector store.
    4. Saves document and chunk metadata in the relational database.
    
    Returns the document ID.
    """
    logger.info(f"Starting ingestion for PDF: {filename} from {file_path}")
    
    # Read PDF using pypdf
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        logger.info(f"Loaded PDF with {total_pages} pages.")
    except Exception as e:
        logger.error(f"Failed to read PDF file: {e}")
        raise ValueError(f"Could not read PDF file: {e}")

    # Extract pages to LangChain Documents
    documents = []
    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        text = page.extract_text() or ""
        if text.strip():
            doc = Document(
                page_content=text,
                metadata={
                    "filename": filename,
                    "page": page_num
                }
            )
            documents.append(doc)
            
    if not documents:
        raise ValueError("The PDF document does not contain any extractable text.")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    splits = text_splitter.split_documents(documents)
    logger.info(f"Split PDF into {len(splits)} chunks.")

    # Save to databases
    with get_db() as db:
        user = get_or_create_default_user(db)
        
        # 1. Create DBDocument record
        db_doc = DBDocument(
            id=str(uuid.uuid4()),
            user_id=user.id,
            filename=filename,
            file_path=file_path,
            total_pages=total_pages
        )
        db.add(db_doc)
        db.flush()  # Get db_doc.id
        
        # Create langchain documents for vector store and db records
        vector_docs = []
        vector_ids = []
        
        for idx, split in enumerate(splits):
            chroma_id = f"{db_doc.id}_{idx}"
            
            # Prepare metadata for ChromaDB (must contain basic types only)
            chroma_metadata = {
                "document_id": db_doc.id,
                "filename": filename,
                "page": int(split.metadata.get("page", 1)),
                "chunk_index": idx
            }
            
            # Update split metadata for chroma
            split.metadata = chroma_metadata
            vector_docs.append(split)
            vector_ids.append(chroma_id)
            
            # 2. Create DBDocumentChunk record
            db_chunk = DBDocumentChunk(
                id=str(uuid.uuid4()),
                document_id=db_doc.id,
                chunk_index=idx,
                page_number=chroma_metadata["page"],
                chunk_text=split.page_content,
                chroma_id=chroma_id
            )
            db.add(db_chunk)
            
        # 3. Add to ChromaDB vector store
        logger.info(f"Adding chunks to ChromaDB...")
        vectorstore = get_vectorstore()
        vectorstore.add_documents(documents=vector_docs, ids=vector_ids)
        
        # Commit relational DB transaction
        db.commit()
        logger.info(f"Ingestion successful! Relational DB and ChromaDB synchronized. Doc ID: {db_doc.id}")
        return db_doc.id
