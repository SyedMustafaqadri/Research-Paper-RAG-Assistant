import os
import shutil
from pathlib import Path
from core.config import Config
from core.logger import logger
from database.connection import get_db
from database.models import Document as DBDocument, DocumentChunk as DBDocumentChunk
from rag.ingest import ingest_pdf
from rag.vectorstore import get_vectorstore

class DocumentService:
    @staticmethod
    def get_all_documents():
        """Retrieve all documents from database."""
        with get_db() as db:
            return db.query(DBDocument).order_by(DBDocument.upload_date.desc()).all()

    @staticmethod
    def get_document(doc_id: str):
        """Retrieve a specific document by its ID."""
        with get_db() as db:
            return db.query(DBDocument).filter_by(id=doc_id).first()

    @staticmethod
    def register_and_ingest(file_name: str, src_path: str) -> str:
        """
        Copies file to upload folder, triggers ingestion, and logs results.
        """
        # Generate destination path
        dest_dir = Path(Config.UPLOAD_FOLDER_ABS)
        os.makedirs(dest_dir, exist_ok=True)
        
        # Keep name clean but unique if needed
        dest_path = dest_dir / file_name
        
        logger.info(f"Copying uploaded file to {dest_path}")
        shutil.copy(src_path, dest_path)
        
        # Ingest PDF into RAG pipeline
        doc_id = ingest_pdf(str(dest_path), file_name)
        return doc_id

    @staticmethod
    def delete_document(doc_id: str) -> bool:
        """
        Deletes a document from the local filesystem, vector store, and relational db.
        """
        logger.info(f"Deleting document {doc_id}")
        
        with get_db() as db:
            doc = db.query(DBDocument).filter_by(id=doc_id).first()
            if not doc:
                logger.warning(f"Document {doc_id} not found in database.")
                return False
            
            # 1. Delete file from local filesystem
            if os.path.exists(doc.file_path):
                try:
                    os.remove(doc.file_path)
                    logger.info(f"Deleted local file: {doc.file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete local file: {e}")
            
            # 2. Delete from ChromaDB
            try:
                vectorstore = get_vectorstore()
                # LangChain Chroma delete by filter
                vectorstore.delete(where={"document_id": doc_id})
                logger.info(f"Deleted vectors for document {doc_id} from ChromaDB")
            except Exception as e:
                logger.error(f"Failed to delete vectors from ChromaDB: {e}")
            
            # 3. Delete from relational DB (cascades to chunks)
            db.delete(doc)
            db.commit()
            logger.info(f"Deleted database records for document {doc_id}")
            return True
