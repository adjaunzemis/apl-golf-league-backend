"""
Scheduled Task Router
"""

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

import datetime

from ..scheduler import app as app_scheduler

session = app_scheduler.session

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

class Task(BaseModel):
    name: str
    description: Optional[str]
    priority: int

    start_cond: str
    end_cond: str
    timeout: Optional[int]

    disabled: bool
    force_termination: bool
    force_run: bool

    status: str
    is_running: bool
    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]
    last_terminate: Optional[datetime.datetime]
    last_inaction: Optional[datetime.datetime]
    last_crash: Optional[datetime.datetime]
    
@router.get("/", response_model=List[Task])
async def get_tasks():
    return [
        Task(
            start_cond=str(task.start_cond), 
            end_cond=str(task.end_cond),
            is_running=task.is_running,
            **task.dict(exclude={'start_cond', 'end_cond'})
        )
        for task in session.tasks
    ]
