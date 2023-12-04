import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from Database.models import Base

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)

# Create tables in the database if they do not exist
print("Creating tables...")
Base.metadata.create_all(bind=engine, checkfirst=True)
print("Tables created successfully")

Session = scoped_session(sessionmaker(bind=engine))
