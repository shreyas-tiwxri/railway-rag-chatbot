from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    generation_model: str = "llama-3.1-8b-instant"
    chroma_persist_dir: str = "./data/chroma"
    sqlite_db_path: str = "./data/railway_docs.db"
    raw_pdf_dir: str = "./data/raw_pdfs"

    class Config:
        env_file = ".env"


settings = Settings()
