from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Explicitly load .env from backend directory using absolute path
# The .env file is in the backend directory (two levels up from app/core)
ENV_PATH = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(dotenv_path=ENV_PATH)

# Debug logging
print(f"Loading .env from: {ENV_PATH}")
print(f"File exists: {os.path.exists(ENV_PATH)}")
print(f"GEMINI_API_KEY detected: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
print(f"Raw env var: {repr(os.getenv('GEMINI_API_KEY'))}")

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str
    
    # Database
    chroma_db_path: str = "./chroma_db"
    
    # Text Processing
    chunk_size: int = 500
    chunk_overlap: int = 100
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: str = "pdf,docx,txt"
    
    def get_allowed_file_types_list(self) -> List[str]:
        return [type.strip() for type in self.allowed_file_types.split(',')]
    
    class Config:
        env_file = ENV_PATH
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

# Debug logging for loaded settings
print(f"Settings loaded - API Key: {'Set' if settings.gemini_api_key else 'Missing'}")

# Validate critical settings on startup
if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
    raise ValueError(
        "GEMINI_API_KEY is required. Please set it in your .env file. "
        f"Expected .env file at: {ENV_PATH}\n"
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )
