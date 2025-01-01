from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# Replace the following with your actual PostgreSQL connection string
# For example: postgresql://user:password@localhost:5432/mydatabase
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/user_service")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -----------------------------------------------------------------------------
# SQLAlchemy Model
# -----------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    occupation = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

# Create the table(s) in the database if they don't already exist
Base.metadata.create_all(bind=engine)
