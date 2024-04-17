"""
Task Scheduler
"""

from rocketry import Rocketry
from sqlmodel import Session

from app.dependencies import get_sql_db_engine
from app.tasks.matches import initialize_matches_for_flight

app = Rocketry(execution="async")


@app.task(parameters={"flight_id": -1, "dry_run": False})
async def initialize_flight_schedule(flight_id: int, dry_run: bool):
    with Session(get_sql_db_engine()) as session:
        initialize_matches_for_flight(
            session=session, flight_id=flight_id, dry_run=dry_run
        )


# @app.task(cron("0 23 * * 0"))
# async def run_handicap_update():
#     date_today = datetime.date.today()
#     date_sunday_current = date_today - datetime.timedelta(
#         days=(date_today.weekday() + 1) % 7
#     )
#     date_monday_current = date_sunday_current + datetime.timedelta(days=1)
#     date_monday_previous = date_monday_current - datetime.timedelta(days=7)

#     print(f"Starting handicap update: {date_monday_previous} - {date_monday_current}")

#     # with get_sql_db_session() as session:
#     # recalculate_hole_results(session=session, year=2023)
#     # update_golfer_handicaps(
#     #     session=session,
#     #     old_max_date=OLD_MAX_DATE,
#     #     new_max_date=NEW_MAX_DATE,
#     #     dry_run=DRY_RUN,
#     # )
#     # print("Done!")

#     print(f"Handicap update complete!")


if __name__ == "__main__":
    app.run()
