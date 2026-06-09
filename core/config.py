import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL = os.getenv("APP_DATABASE_URL", "sqlite:///./local.db")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploaded_pdfs")
    ENV = os.getenv("ENV", "development")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

    # Resolve paths relative to root if they are relative
    CHROMA_DB_PATH_ABS = str((PROJECT_ROOT / CHROMA_DB_PATH).resolve()) if not Path(CHROMA_DB_PATH).is_absolute() else CHROMA_DB_PATH
    UPLOAD_FOLDER_ABS = str((PROJECT_ROOT / UPLOAD_FOLDER).resolve()) if not Path(UPLOAD_FOLDER).is_absolute() else UPLOAD_FOLDER

    @classmethod
    def validate(cls):
        """Validates that critical configurations are present."""
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError(
                "GOOGLE_API_KEY is not set. Please set it in your .env file or environment variables."
            )
        
        # Ensure directories exist
        os.makedirs(cls.UPLOAD_FOLDER_ABS, exist_ok=True)
        os.makedirs(os.path.dirname(cls.CHROMA_DB_PATH_ABS), exist_ok=True)

# Run basic validation warnings on import if debug
if Config.DEBUG:
    try:
        # Don't fail immediately on import to allow running tests or other tasks without API key
        if not Config.GOOGLE_API_KEY or Config.GOOGLE_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("[WARNING] GOOGLE_API_KEY is not configured in .env file.")
    except Exception as e:
        print(f"[ERROR] Failed config check: {e}")
