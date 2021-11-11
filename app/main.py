from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies import create_db_and_tables
from .routers import courses, golfers, rounds, flights, matches

description = """
APLGolfLeague API
"""

app = FastAPI(
    title="APLGolfLeague",
    description=description,
    version="0.1.0",
    contact={
        "name": "Andris Jaunzemis",
        "email": "adjaunzemis@gmail.com",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router)
app.include_router(golfers.router)
app.include_router(rounds.router)
app.include_router(flights.router)
app.include_router(matches.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
