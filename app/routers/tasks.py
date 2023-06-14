"""
Scheduled Task Router
"""

import datetime
import fastapi
import pydantic
from typing import List, Optional

from ..scheduler import app as app_scheduler

session = app_scheduler.session

router = fastapi.APIRouter(prefix="/tasks", tags=["Tasks"])


class Task(pydantic.BaseModel):
    name: str
    description: Optional[str]
    priority: int

    start_cond: str
    end_cond: str
    timeout: Optional[int]

    disabled: bool
    force_termination: bool
    force_run: bool

    status: Optional[str]
    is_running: bool
    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]
    last_terminate: Optional[datetime.datetime]
    last_inaction: Optional[datetime.datetime]
    last_crash: Optional[datetime.datetime]


def serialize_task(task: Task):
    return Task(
        start_cond=str(task.start_cond),
        end_cond=str(task.end_cond),
        is_running=task.is_running,
        **task.dict(exclude={"start_cond", "end_cond"}),
    )


@router.get("/", response_model=List[Task])
async def list_tasks():
    return [serialize_task(task) for task in session.tasks]


@router.get("/{task_name}", response_model=Task)
async def get_task(task_name: str = fastapi.Path(..., description="Task name")):
    try:
        task = session[task_name]
        return serialize_task(task)
    except KeyError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task name: '{task_name}'",
        )


@router.post("/run")
async def run_task(task_name: str = fastapi.Query(..., description="Task name to run")):
    try:
        task = session[task_name]
        task.run()
        return {"detail": f"Executing task: '{task_name}'"}
    except KeyError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid task name: '{task_name}'",
        )
