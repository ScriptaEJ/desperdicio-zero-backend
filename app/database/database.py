from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL_DOCKER = os.getenv("DB_URL_DOCKER")

if not DB_URL_DOCKER:
    raise ValueError("DB_URL_DOCKER não configurada")

engine = create_engine(DB_URL_DOCKER)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()