from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .dependencies import create_db_and_tables, log_request_data
from .routers import courses, golfers, teams, flights, tournaments, divisions, rounds, matches, handicapping, officers

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
