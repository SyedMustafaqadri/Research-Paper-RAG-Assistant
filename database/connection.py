from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from contextlib import contextmanager
from core.config import Config
from core.logger import logger

# Create SQLAlchemy engine
engine = create_engine(
    Config.DATABASE_URL,
    # SQLite-specific arguments (connect_args) if using SQLite
    connect_args={"check_same_thread": False} if Config.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initializes the database tables."""
    try:
        logger.info("Initializing relational database tables...")
        # Import models here to ensure they are registered with Base
        import database.models
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise e

@contextmanager
def get_db():
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
