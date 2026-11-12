import json

from rocketry import Rocketry
from sqlmodel import Session

from app.dependencies import get_sql_db_engine
from app.tasks.matches import initialize_matches_for_flight

app = Rocketry(execution="async")


@app.task(
    parameters={
        "flight_id": -1,
        "bye_weeks_by_team": None,
        "dry_run": False,
        "force": False,
    }
)
async def initialize_flight_schedule(
    flight_id: int, bye_weeks_by_team: str | None, dry_run: bool, force: bool
):
    if bye_weeks_by_team is None:
        bye_week_requests = None
    else:
        bye_week_requests = {
            int(team): int(week) for team, week in json.loads(bye_weeks_by_team).items()
        }

    with Session(get_sql_db_engine()) as session:
        initialize_matches_for_flight(
            session=session,
            flight_id=flight_id,
            bye_weeks_by_team=bye_week_requests,
            dry_run=dry_run,
            force=force,
        )


if __name__ == "__main__":
    app.run()
