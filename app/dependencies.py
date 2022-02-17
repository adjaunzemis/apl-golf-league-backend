import sys
import os
from dotenv import load_dotenv
from fastapi import Request
from sqlmodel import SQLModel, Session, create_engine
from loguru import logger

load_dotenv()

DATABASE_USER = os.environ.get("APLGL_DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("APLGL_DATABASE_PASSWORD")
DATABASE_ADDRESS = os.environ.get("APLGL_DATABASE_ADDRESS")
DATABASE_PORT = os.environ.get("APLGL_DATABASE_PORT")
DATABASE_NAME = os.environ.get("APLGL_DATABASE_NAME")
DATABASE_ECHO = os.environ.get("APLGL_DATABASE_ECHO").lower() == 'true'

DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:{DATABASE_PORT}/{DATABASE_NAME}"
engine = create_engine(DATABASE_URL, echo=DATABASE_ECHO)

logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>")

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

async def log_request_data(request: Request):
    """
    Logs request with parameters and headers.

    Included as router-level dependency.

    Parameters
    ----------
    request : Request
        request to log
    
    References
    ----------
    https://stackoverflow.com/questions/63400683/python-logging-with-loguru-log-request-params-on-fastapi-app

    """
    logger.debug(f"{request.method} {request.url}")
    logger.debug("Params:")
    for name, value in request.path_params.items():
        logger.debug(f"\t{name}: {value}")
    logger.debug("Headers:")
    for name, value in request.headers.items():
        logger.debug(f"\t{name}: {value}")
    # TODO: Log request body, handle errors when request has no body
    # req_body = await request.json()
    # if req_body:
    #     logger.debug(f"Body:")
    #     logger.debug(f"\t{req_body}")
