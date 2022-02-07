from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from .dependencies import create_db_and_tables
from .routers import courses, golfers, teams, flights, tournaments, divisions, rounds, matches, handicapping

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

app.include_router(courses.router)
app.include_router(golfers.router)
app.include_router(teams.router)
app.include_router(flights.router)
app.include_router(tournaments.router)
app.include_router(divisions.router)
app.include_router(rounds.router)
app.include_router(matches.router)
app.include_router(handicapping.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

handler = Mangum(app)
