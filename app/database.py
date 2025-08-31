# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# Use PostgreSQL for production, SQLite for development
DATABASE_URL = "sqlite:///./local_dev.db"

engine = create_engine(
	DATABASE_URL, connect_args={"check_same_thread": False}
)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()