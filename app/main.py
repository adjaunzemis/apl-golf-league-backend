from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import logging

from .dependencies import create_db_and_tables
from .routers import courses, golfers, teams, flights, tournaments, divisions, rounds, matches, handicapping, officers
from .utilities.custom_logger import CustomizeLogger

description = """
APL Golf League API
"""

app = FastAPI(
    title="APL Golf League",
    description=description,
    version="0.1.0",
    contact={
        "name": "Andris Jaunzemis",
        "email": "adjaunzemis@gmail.com",
    }
)

CONFIG_PATH = "logs/logging.config"
logger = logging.getLogger(__name__)
logger = CustomizeLogger.make_logger(CONFIG_PATH)
app.logger = logger

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router, dependencies=[Depends(log_request_data)])
app.include_router(golfers.router, dependencies=[Depends(log_request_data)])
app.include_router(teams.router, dependencies=[Depends(log_request_data)])
app.include_router(flights.router, dependencies=[Depends(log_request_data)])
app.include_router(tournaments.router, dependencies=[Depends(log_request_data)])
app.include_router(divisions.router, dependencies=[Depends(log_request_data)])
app.include_router(rounds.router, dependencies=[Depends(log_request_data)])
app.include_router(matches.router, dependencies=[Depends(log_request_data)])
app.include_router(officers.router, dependencies=[Depends(log_request_data)])
app.include_router(handicapping.router, dependencies=[Depends(log_request_data)])

@app.get('/')
def hello_world(log = Depends(log_request_data)):
    return {"message": "Hello from APLGolfLeagueAPI!"}

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

handler = Mangum(app)
