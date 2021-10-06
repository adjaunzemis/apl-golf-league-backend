from fastapi import FastAPI

from .dependencies import create_db_and_tables
from .routers import courses, golfers

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

app.include_router(courses.router)
app.include_router(golfers.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
