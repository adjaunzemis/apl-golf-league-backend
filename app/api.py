"""
FastAPI Application
"""

import logging
import tomllib
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Dict, List

from fastapi import BackgroundTasks, Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from starlette.responses import JSONResponse

from app.dependencies import (
    close_nosql_db,
    create_nosql_db_and_collections,
    create_sql_db_and_tables,
    get_nosql_db_client,
)
from app.routers import (
    courses,
    flights,
    golfers,
    handicaps,
    matches,
    officers,
    payments,
    rounds,
    seasons,
    tasks,
    teams,
    tournaments,
    users,
)
from app.utilities.custom_logger import CustomizeLogger
from app.utilities.notifications import EmailSchema, send_email


@lru_cache
def _get_project_info():
    with open("pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return {
        "name": data.get("project", {}).get("name", "Unknown"),
        "version": data.get("project", {}).get("version", "Unknown"),
        "description": data.get("project", {}).get("description", "Unknown"),
        "authors": data.get("project", {}).get("authors", []),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_sql_db_and_tables()
    create_nosql_db_and_collections()
    yield
    close_nosql_db()


app = FastAPI(
    title=_get_project_info()["name"],
    description=_get_project_info()["description"],
    version=_get_project_info()["version"],
    contact={
        "name": _get_project_info()["authors"][0]["name"],
        "email": _get_project_info()["authors"][0]["email"],
    },
    lifespan=lifespan,
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
app.include_router(seasons.router, dependencies=[Depends(log_request_data)])
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
    send_email(email, "handicap_update_report.html", background_tasks)
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Email has been sent"}
    )


if __name__ == "__main__":
    app.run()
