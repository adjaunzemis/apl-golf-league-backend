from fastapi import FastAPI

from .dependencies import create_db_and_tables
from .routers import courses

app = FastAPI()

app.include_router(courses.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
