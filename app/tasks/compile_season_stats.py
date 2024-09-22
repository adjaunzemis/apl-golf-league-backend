from datetime import datetime, timedelta
from typing import List

import numpy as np
import pandas as pd
import pytz
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, select

from app.dependencies import get_settings
from app.models.golfer import Golfer
from app.models.round import RoundSummary, RoundType
from app.tasks.handicaps import (
    get_handicap_index_data,
    get_rounds_in_scoring_record,
)


def get_rounds_for_golfer(*, session: Session, year: int, golfer_db: Golfer):
    """
    Gets all rounds played by the given golfer in the given year.
    """
    rounds_db = get_rounds_in_scoring_record(
        session=session,
        golfer_id=golfer_db.id,
        min_date=datetime(year, 1, 1),
        max_date=datetime(year + 1, 1, 1),
        limit=None,
        use_legacy_handicapping=False,
    )
    if (rounds_db is None) or (len(rounds_db) == 0):
        return None
    return rounds_db


def filter_rounds(
    *,
    rounds_db: List[RoundSummary],
    include_tournaments: bool = False,
    include_playoffs: bool = False,
    playoffs_start_date: datetime = datetime.now(),
):
    """
    Filters rounds to those to be used for statistics.
    """
    flight_rounds_db = [
        round_db
        for round_db in rounds_db
        if round_db.round_type == RoundType.FLIGHT
        and round_db.date_played < playoffs_start_date
    ]
    filtered_rounds_db = flight_rounds_db

    tournament_rounds_db = [
        round_db
        for round_db in rounds_db
        if round_db.round_type == RoundType.TOURNAMENT
    ]
    if include_tournaments:
        filtered_rounds_db.extend(tournament_rounds_db)

    playoff_rounds_db = [
        round_db
        for round_db in rounds_db
        if round_db.round_type == RoundType.PLAYOFF
        or (
            round_db.round_type == RoundType.FLIGHT
            and round_db.date_played >= playoffs_start_date
        )
    ]
    if include_playoffs:
        filtered_rounds_db.extend(playoff_rounds_db)

    print(
        f"\tFlights: {len(flight_rounds_db)}, Tournaments: {len(tournament_rounds_db)}, Playoffs: {len(playoff_rounds_db)}"
    )
    if (not filtered_rounds_db) or (len(filtered_rounds_db) == 0):
        return None
    return filtered_rounds_db


def compile_season_statistics(*, session: Session, year: int):
    """ """
    print(f"Compiling season statistics for {year}")

    SEASON_START_DATE = datetime(year, 4, 1, tzinfo=pytz.UTC)  # TODO: un-hardcode
    PLAYOFFS_START_DATE = datetime(year, 9, 4, tzinfo=pytz.UTC)  # TODO: un-hardcode
    rounds = {}
    stats = {}

    # Get all rounds played by each golfer in the given year
    golfers_db = session.exec(select(Golfer)).all()
    for golfer_db in golfers_db:
        rounds_db = get_rounds_for_golfer(
            session=session, year=year, golfer_db=golfer_db
        )
        if rounds_db:
            print(
                f"Golfer '{golfer_db.name}' (id={golfer_db.id}) played {len(rounds_db)} rounds in {year}"
            )

            # Compile round summary data
            for round_db in rounds_db:
                if round_db.round_type != RoundType.QUALIFYING:
                    rounds[len(rounds)] = {
                        "golfer_id": golfer_db.id,
                        "golfer_name": golfer_db.name,
                        "golfer_playing_handicap": round_db.golfer_playing_handicap,
                        "round_type": round_db.round_type,
                        "round_date": round_db.date_played,
                        "course_name": round_db.course_name,
                        "track_name": round_db.track_name,
                        "tee_name": round_db.tee_name,
                        "tee_par": round_db.tee_par,
                        "tee_rating": round(round_db.tee_rating, 2),
                        "tee_slope": round_db.tee_slope,
                        "gross_score": round_db.gross_score,
                        "gross_to_par": round_db.gross_score - round_db.tee_par,
                        "gross_differential": round(round_db.score_differential, 3),
                        "net_score": round_db.net_score,
                        "net_to_par": round_db.net_score - round_db.tee_par,
                        "net_differential": round(
                            round_db.score_differential
                            - round_db.golfer_playing_handicap,
                            3,
                        ),
                    }

            # Filter to statistics-relevant rounds (exclude tournaments and playoffs)
            filtered_rounds_db = filter_rounds(
                rounds_db=rounds_db, playoffs_start_date=PLAYOFFS_START_DATE
            )
            if filtered_rounds_db:
                print(f"\tCompiling statistics using {len(filtered_rounds_db)} rounds")

                # Determine golfer starting handicap index
                golfer_starting_handicap = get_handicap_index_data(
                    session=session,
                    golfer_id=golfer_db.id,
                    min_date=datetime(year - 2, 1, 1).date(),
                    max_date=SEASON_START_DATE.date(),
                    limit=10,
                    include_rounds=True,
                )

                if golfer_starting_handicap.active_handicap_index is None:
                    # Check for qualifying scores entered after season start
                    print(f"WARNING: Expanding starting handicap search into season")
                    first_round = sorted(
                        filtered_rounds_db, key=lambda r: r.date_played
                    )[0]
                    golfer_starting_handicap = get_handicap_index_data(
                        session=session,
                        golfer_id=golfer_db.id,
                        min_date=datetime(year - 2, 1, 1).date(),
                        max_date=(first_round.date_played - timedelta(days=1)).date(),
                        limit=10,
                        include_rounds=True,
                    )

                    if golfer_starting_handicap.active_handicap_index is None:
                        print(
                            f"WARNING: No starting handicap found - using first playing handicap to calculate"
                        )
                        golfer_starting_handicap.active_handicap_index = (
                            first_round.golfer_playing_handicap
                            - (first_round.tee_rating - first_round.tee_par)
                        ) / (first_round.tee_slope / 113)

                # Determine golfer current/ending handicap index
                golfer_current_handicap = get_handicap_index_data(
                    session=session,
                    golfer_id=golfer_db.id,
                    min_date=datetime(year - 2, 1, 1).date(),
                    max_date=datetime.today().date(),
                    limit=10,
                    include_rounds=True,
                )

                # Compile golfer season statistics
                stats[len(stats)] = {
                    "golfer_id": golfer_db.id,
                    "name": golfer_db.name,
                    "starting_handicap_index": round(
                        golfer_starting_handicap.active_handicap_index, 1
                    ),
                    "current_handicap_index": round(
                        golfer_current_handicap.active_handicap_index, 1
                    ),
                    "rounds_played": len(filtered_rounds_db),
                    "avg_gross_to_par": round(
                        np.mean(
                            [
                                (round_db.gross_score - round_db.tee_par)
                                for round_db in filtered_rounds_db
                            ]
                        ),
                        3,
                    ),
                    "avg_gross_differential": round(
                        np.mean(
                            [
                                round_db.score_differential
                                for round_db in filtered_rounds_db
                            ]
                        ),
                        3,
                    ),
                    "avg_net_to_par": round(
                        np.mean(
                            [
                                (round_db.net_score - round_db.tee_par)
                                for round_db in filtered_rounds_db
                            ]
                        ),
                        3,
                    ),
                    "avg_net_differential": round(
                        np.mean(
                            [
                                (
                                    round_db.score_differential
                                    - round_db.golfer_playing_handicap
                                )
                                for round_db in filtered_rounds_db
                            ]
                        ),
                        3,
                    ),
                }

    # Save round summaries to file
    rounds_filename = f"APLGolfLeague_Rounds_{year}.csv"
    rounds_df = pd.DataFrame(rounds)
    rounds_df = rounds_df.transpose()
    rounds_df.to_csv(rounds_filename)
    print(f"Saved rounds to file: {rounds_filename}")

    # Save season statistics to file
    stats_filename = f"APLGolfLeague_SeasonStats_{year}.csv"
    stats_df = pd.DataFrame(stats)
    stats_df = stats_df.transpose()
    stats_df.to_csv(stats_filename)
    print(f"Saved season statistics to file: {stats_filename}")


if __name__ == "__main__":
    load_dotenv()

    settings = get_settings()

    DB_URL = settings.apl_golf_league_api_url
    DB_PORT = (
        settings.apl_golf_league_api_database_port_external
    )  # NOTE: using external port, not running from inside container
    db_uri = f"{settings.apl_golf_league_api_database_connector}://{settings.apl_golf_league_api_database_user}:{settings.apl_golf_league_api_database_password}@{DB_URL}:{DB_PORT}/{settings.apl_golf_league_api_database_name}"

    engine = create_engine(db_uri, echo=False)
    YEAR = 2024  # TODO: un-hardcode year for analysis

    with Session(engine) as session:
        compile_season_statistics(session=session, year=YEAR)
    print("Done!")
