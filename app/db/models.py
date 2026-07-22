"""
SQLite schema for:
1. `documents` — metadata about each ingested PDF
2. `rate_table` — long-format structured rows extracted from rate/tariff tables,
   used for exact numeric lookups instead of vector search.

Why long-format? Every table in these Railway docs follows the same shape:
scale name x distance-slab x weight-slab -> rate. Normalizing all of them into
one table means new PDFs with the same table shape need zero schema changes.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from app.config import settings

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, nullable=False)
    title = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    num_pages = Column(Integer, nullable=True)
    ingested_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending | processing | done | failed


class RateTableRow(Base):
    __tablename__ = "rate_table"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, nullable=False)
    filename = Column(String, nullable=True)     # source document, for citations
    scale = Column(String, index=True)          # e.g. "Scale-R", "Scale-P", "Scale-S", "Scale-L"
    category = Column(String, nullable=True)    # e.g. "Luggage", "Premier Parcel", "Standard Parcel"
    distance_min_km = Column(Integer, index=True)
    distance_max_km = Column(Integer, index=True)
    weight_slab_kg = Column(Integer, index=True)  # upper bound of weight bracket, e.g. 10, 20, 30...
    rate_rs = Column(Float)
    page_number = Column(Integer, nullable=True)


engine = create_engine(f"sqlite:///{settings.sqlite_db_path}")
SessionLocal = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)
