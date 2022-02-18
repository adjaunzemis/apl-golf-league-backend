import sys
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DATABASE_USER = os.environ.get("APLGL_DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("APLGL_DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("APLGL_DATABASE_ADDRESS")
DATABASE_PORT = os.environ.get("APLGL_DATABASE_PORT")
DATABASE_NAME = os.environ.get("APLGL_DATABASE_NAME")
DATABASE_ECHO = os.environ.get("APLGL_DATABASE_ECHO").lower() == 'true'

DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
