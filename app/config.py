from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groq_api_key: str = ""
    generation_model: str = "llama-3.3-70b-versatile"
    tesseract_cmd: str = ""  # e.g. C:\Program Files\Tesseract-OCR\tesseract.exe on Windows
    chroma_persist_dir: str = "./data/chroma"
    sqlite_db_path: str = "./data/railway_docs.db"
    raw_pdf_dir: str = "./data/raw_pdfs"

    class Config:
        env_file = ".env"


settings = Settings()
