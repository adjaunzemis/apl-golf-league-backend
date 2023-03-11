"""
FastAPI Application
"""

from fastapi import Depends, FastAPI, Request, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from pymongo import MongoClient
import logging

from typing import List, Dict

from .dependencies import (
    create_sql_db_and_tables,
    create_nosql_db_and_collections,
    close_nosql_db,
    get_nosql_db_client,
)
from .routers import (
    courses,
    golfers,
    teams,
    flights,
    tournaments,
    rounds,
    matches,
    handicaps,
    officers,
    users,
    payments,
    tasks,
)
from .utilities.custom_logger import CustomizeLogger
from .utilities.notifications import EmailSchema, send_email

description = """
APL Golf League API
"""

app = FastAPI(
    title="APL Golf League",
    description=description,
    version="0.4.0",
    contact={
        "name": "Andris Jaunzemis",
        "email": "adjaunzemis@gmail.com",
    },
)

CONFIG_PATH = "app/logging.config"
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


@app.get("/")
async def get_info():
    """
    Returns API info.
    """
    return {"title": app.title, "description": app.description, "version": app.version}


@app.get("/heartbeat/", tags=["Heartbeat"])
async def get_heartbeat():
    """
    Heartbeat for checking connection to API.
    """
    return {"status": "alive"}


app.include_router(tasks.router, dependencies=[Depends(log_request_data)])
app.include_router(users.router, dependencies=[Depends(log_request_data)])
app.include_router(courses.router, dependencies=[Depends(log_request_data)])
app.include_router(golfers.router, dependencies=[Depends(log_request_data)])
app.include_router(teams.router, dependencies=[Depends(log_request_data)])
app.include_router(flights.router, dependencies=[Depends(log_request_data)])
app.include_router(tournaments.router, dependencies=[Depends(log_request_data)])
app.include_router(rounds.router, dependencies=[Depends(log_request_data)])
app.include_router(matches.router, dependencies=[Depends(log_request_data)])
app.include_router(officers.router, dependencies=[Depends(log_request_data)])
app.include_router(handicaps.router, dependencies=[Depends(log_request_data)])
app.include_router(payments.router, dependencies=[Depends(log_request_data)])


@app.on_event("startup")
def on_startup():
    create_sql_db_and_tables()


@app.on_event("startup")
def startup_db_client():
    create_nosql_db_and_collections()


@app.on_event("shutdown")
def on_shutdown():
    close_nosql_db()


@app.get("/mongodb_test/", response_model=List[Dict])
async def test_nosql_db(*, client: MongoClient = Depends(get_nosql_db_client)):
    DB_NAME = "TestDB"
    return list(
        client[DB_NAME]["TestCollection"].find(projection={"_id": False}, limit=100)
    )


@app.post("/email_test/")
async def test_email(
    *, email: EmailSchema, background_tasks: BackgroundTasks
) -> JSONResponse:
    send_email(email, "email.html", background_tasks)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Email has been sent"}
    )


if __name__ == "__main__":
    app.run()
