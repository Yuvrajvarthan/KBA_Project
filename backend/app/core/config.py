from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the backend directory
load_dotenv()

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
    allowed_file_types: List[str] = ["pdf", "docx", "txt"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Validate critical settings on startup
if not settings.gemini_api_key or settings.gemini_api_key == "your_gemini_api_key_here":
    raise ValueError(
        "GEMINI_API_KEY is required. Please set it in your .env file. "
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )
