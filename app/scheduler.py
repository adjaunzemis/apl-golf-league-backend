import datetime
import json

from rocketry import Rocketry
from rocketry.conds import cron
from sqlmodel import Session, select

from app.dependencies import get_sql_db_engine
from app.models.officer import Officer
from app.tasks.handicaps import update_golfer_handicaps
from app.tasks.matches import initialize_matches_for_flight
from app.utilities.notifications import EmailSchema, send_email

app = Rocketry(execution="async")


@app.task(parameters={"flight_id": -1, "bye_weeks_by_team": None, "dry_run": False})
async def initialize_flight_schedule(
    flight_id: int, bye_weeks_by_team: str | None, dry_run: bool
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
        )


@app.task(
    cron("0 23 * * 0"),
    parameters={"golfer_id": None, "force_update": False, "dry_run": False},
)
async def run_handicap_update(golfer_id: int | None, force_update: bool, dry_run: bool):
    # TODO: Allow input of date range
    date_today = datetime.date.today()
    date_sunday_current = date_today - datetime.timedelta(
        days=(date_today.weekday() + 1) % 7
    )
    date_monday_current = date_sunday_current + datetime.timedelta(days=1)
    date_monday_previous = date_monday_current - datetime.timedelta(days=7)

    update_start = datetime.datetime.now()
    with Session(get_sql_db_engine()) as session:
        updates_info = update_golfer_handicaps(
            session=session,
            golfer_id=golfer_id,
            prior_end_date=date_monday_previous,
            new_end_date=date_monday_current,
            force_update=force_update,
            dry_run=dry_run,
        )
        handicappers = session.exec(
            select(Officer)
            .where(Officer.year == update_start.year)
            .where(Officer.role == "Handicapper")
        ).all()

    if len(handicappers) > 0:
        print("Sending handicap update report to handicappers...")
        email = EmailSchema(
            subject=f"[APL Golf League] Handicap Update Report - {update_start.date().isoformat()}",
            to_addresses=[hc.email for hc in handicappers if hc.email is not None],
            body={
                "update_date": update_start.replace(microsecond=0).isoformat(),
                "updates": updates_info,
            },
        )
        await send_email(email=email, template_name="handicap_update_report.html")


if __name__ == "__main__":
    app.run()
