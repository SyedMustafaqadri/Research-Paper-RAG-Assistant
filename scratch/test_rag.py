import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.config import Config
from core.logger import logger
from database.connection import init_db, get_db
from database.models import User
from rag.embeddings import get_embeddings
from rag.vectorstore import get_vectorstore
from graph.workflow import graph_app

def run_tests():
    logger.info("Starting verification tests...")

    # 1. Config Loading Verification
    logger.info("1. Verifying config...")
    logger.info(f"PROJECT_ROOT: {Config.PROJECT_ROOT}")
    logger.info(f"DATABASE_URL: {Config.DATABASE_URL}")
    logger.info(f"CHROMA_DB_PATH: {Config.CHROMA_DB_PATH_ABS}")
    logger.info(f"UPLOAD_FOLDER: {Config.UPLOAD_FOLDER_ABS}")

    # 2. Database Initialization Verification
    logger.info("2. Verifying database connection and schema...")
    init_db()
    with get_db() as db:
        # Check if we can query users
        users = db.query(User).all()
        logger.info(f"Query successful. Found {len(users)} users.")

    # 3. Vectorstore and Embeddings Import Verification
    logger.info("3. Verifying Vectorstore & Embeddings initialization...")
    try:
        # Just create the references without invoking API (in case key is missing during tests)
        vectorstore = get_vectorstore()
        logger.info("Vector store class initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not fully initialize vectorstore (this is expected if GOOGLE_API_KEY is not set): {e}")

    # 4. LangGraph Workflow Compile Verification
    logger.info("4. Verifying LangGraph workflow compilation...")
    try:
        # Verify compiled graph structure
        nodes = graph_app.get_graph().nodes
        logger.info(f"Graph compiled successfully with nodes: {list(nodes.keys())}")
    except Exception as e:
        logger.error(f"LangGraph compile failed: {e}")
        sys.exit(1)

    logger.info("All import, compilation, and DB structure checks passed!")

if __name__ == "__main__":
    run_tests()
