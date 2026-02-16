from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # 1. Project Paths
    # This automatically finds the root folder regardless of where you run the script
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    # 2. Project Metadata
    app_name: str = "SPJIMR Sustainability Dashboard"
    debug: bool = True

    # 3. File Paths (Relative to root)
    # This matches the folder structure we built
    excel_path: str = "data/raw/campus_data.xlsx"
    upload_dir: str = "uploads"

    # 4. API Keys (Placeholders - will be read from your .env file)
    # If these are not in your .env, Pydantic will throw a clear error
    openai_api_key: str = "default_key" 
    google_api_key: str = "default_key"
    huggingface_token: str = "default_key"

    # 5. Model Configuration (For Phase 2)
    primary_model: str = "gpt-4o"
    embedding_model: str = "all-MiniLM-L6-v2"

    # This tells Python to look for a .env file in the root
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Initialize the settings object to be imported by other files
settings = Settings()