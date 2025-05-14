from sqlmodel import Session, select

from app.models.flight import Flight
from app.models.flight_team_link import FlightTeamLink
from app.models.match import Match


def initialize_matches_for_flight(
    *,
    session: Session,
    flight_id: int,
    bye_weeks_by_team: dict[int, int] | None = None,
    dry_run: bool = False,
):
    flight_db = session.get(Flight, flight_id)
    if flight_db is None:
        raise ValueError(f"Unable to find flight with id={flight_id}")

    print(f"Initializing matches for flight: '{flight_db.name} ({flight_db.year})'")
    if dry_run:
        print(f"NOTE: Dry-run, won't commit changes to database!")

    flight_team_links_db = session.exec(
        select(FlightTeamLink).where(FlightTeamLink.flight_id == flight_db.id)
    ).all()
    if (not flight_team_links_db) or (len(flight_team_links_db) == 0):
        raise ValueError(
            "Unable to find teams in flight: "
            + flight_db.name
            + " ("
            + flight_db.year
            + ")"
        )

    team_ids = [link.team_id for link in flight_team_links_db]

    existing_matches = session.exec(
        select(Match).where(Match.flight_id == flight_id)
    ).all()
    if len(existing_matches) > 0:
        raise ValueError(
            f"Matches already exist for flight: '{flight_db.name} ({flight_db.year})' (id={flight_id})"
        )

    # TODO: Implement other team-number/week-number schedules as needed
    if (flight_db.weeks == 18) and (len(team_ids) == 5):
        matchup_matrix = [  # 5 teams, 18 weeks
            [4, 3, 2, 1, None],  # week 1
            [2, 1, 5, None, 3],  # week 2
            [5, 4, None, 2, 1],  # week 3
            [3, None, 1, 5, 4],  # week 4
            [None, 5, 4, 3, 2],  # week 5
            [4, 3, 2, 1, 4],  # week 6 (extra: 5 vs 4)
            [2, 1, 5, None, 3],  # week 7
            [5, 4, 1, 2, 1],  # week 8 (extra: 3 vs 1)
            [3, None, 1, 5, 4],  # week 9
            [None, 5, 4, 3, 2],  # week 10
            [4, 3, 2, 1, None],  # week 11
            [2, 1, 5, 3, 3],  # week 12 (extra: 4 vs 3)
            [5, 4, None, 2, 1],  # week 13
            [3, 5, 1, 5, 4],  # week 14 (extra: 2 vs 5)
            [None, 5, 4, 3, 2],  # week 15
            [4, 3, 2, 1, None],  # week 16
            [2, 1, 5, None, 3],  # week 17
            [5, 4, None, 2, 1],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 6):
        matchup_matrix = [  # 6 teams, 18 weeks
            [6, 5, 4, 3, 2, 1],  # week 1
            [5, 4, 6, 2, 1, 3],  # week 2
            [4, 3, 2, 1, 6, 5],  # week 3
            [3, 6, 1, 5, 4, 2],  # week 4
            [2, 1, 5, 6, 3, 4],  # week 5
            [6, 5, 4, 3, 2, 1],  # week 6
            [None, None, None, None, None, None],  # week 7
            [5, 4, 6, 2, 1, 3],  # week 8
            [4, 3, 2, 1, 6, 5],  # week 9
            [3, 6, 1, 5, 4, 2],  # week 10
            [2, 1, 5, 6, 3, 4],  # week 11
            [None, None, None, None, None, None],  # week 12
            [6, 5, 4, 3, 2, 1],  # week 13
            [5, 4, 6, 2, 1, 3],  # week 14
            [4, 3, 2, 1, 6, 5],  # week 15
            [3, 6, 1, 5, 4, 2],  # week 16
            [2, 1, 5, 6, 3, 4],  # week 17
            [6, 5, 4, 3, 2, 1],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 7):
        matchup_matrix = [  # 7 teams, 18 weeks
            [6, 5, 4, 3, 2, 1, None],  # week 1
            [5, 4, 7, 2, 1, None, 3],  # week 2
            [4, 3, 2, 1, None, 7, 6],  # week 3
            [3, 7, 1, None, 6, 5, 2],  # week 4
            [2, 1, None, 6, 7, 4, 5],  # week 5
            [7, None, 6, 5, 4, 3, 1],  # week 6
            [None, 6, 5, 7, 3, 2, 4],  # week 7
            [5, 6, 7, 5, 1, 2, 3],  # week 8 (extra: 5 vs 4)
            [4, 3, 2, 1, 7, 1, 5],  # week 9 (extra: 1 vs 6)
            [7, 4, 6, 2, None, 3, 1],  # week 10
            [None, 7, 4, 3, 6, 5, 2],  # week 11
            [2, 1, None, 6, 7, 4, 5],  # week 12
            [7, None, 6, 5, 4, 3, 1],  # week 13
            [None, 6, 5, 7, 3, 2, 4],  # week 14
            [6, 5, 4, 3, 2, 1, None],  # week 15
            [5, 4, 7, 2, 1, None, 3],  # week 16
            [4, 3, 2, 1, None, 7, 6],  # week 17
            [3, 7, 1, None, 6, 5, 2],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 8):
        matchup_matrix = [  # 8 teams, 18 weeks
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 1
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 2
            [6, 5, 4, 3, 2, 1, 8, 7],  # week 3
            [5, 4, 8, 2, 1, 7, 6, 3],  # week 4
            [4, 3, 2, 1, 7, 8, 5, 6],  # week 5
            [3, 8, 1, 7, 6, 5, 4, 2],  # week 6
            [None, None, None, None, None, None, None, None],  # week 7
            [2, 1, 7, 6, 8, 4, 3, 5],  # week 8
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 9
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 10
            [6, 5, 4, 3, 2, 1, 8, 7],  # week 11
            [None, None, None, None, None, None, None, None],  # week 12
            [5, 4, 8, 2, 1, 7, 6, 3],  # week 13
            [4, 3, 2, 1, 7, 8, 5, 6],  # week 14
            [3, 8, 1, 7, 6, 5, 4, 2],  # week 15
            [2, 1, 7, 6, 8, 4, 3, 5],  # week 16
            [8, 7, 6, 5, 4, 3, 2, 1],  # week 17
            [7, 6, 5, 8, 3, 2, 1, 4],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 9):
        matchup_matrix = [  # 9 teams, 18 weeks
            [None, 9, 8, 7, 6, 5, 4, 3, 2],  # week 1
            [9, None, 7, 6, 8, 4, 3, 5, 1],  # week 2
            [8, 7, None, 5, 4, 9, 2, 1, 6],  # week 3
            [7, 6, 5, None, 3, 2, 1, 9, 8],  # week 4
            [6, 8, 4, 3, None, 1, 9, 2, 7],  # week 5
            [5, 4, 9, 2, 1, None, 8, 7, 3],  # week 6
            [4, 3, 2, 1, 9, 8, None, 6, 5],  # week 7
            [3, 5, 1, 9, 2, 7, 6, None, 4],  # week 8
            [2, 1, 6, 8, 7, 3, 5, 4, None],  # week 9
            [None, 9, 8, 7, 6, 5, 4, 3, 2],  # week 10
            [9, None, 7, 6, 8, 4, 3, 5, 1],  # week 11
            [8, 7, None, 5, 4, 9, 2, 1, 6],  # week 12
            [7, 6, 5, None, 3, 2, 1, 9, 8],  # week 13
            [6, 8, 4, 3, None, 1, 9, 2, 7],  # week 14
            [5, 4, 9, 2, 1, None, 8, 7, 3],  # week 15
            [4, 3, 2, 1, 9, 8, None, 6, 5],  # week 16
            [3, 5, 1, 9, 2, 7, 6, None, 4],  # week 17
            [2, 1, 6, 8, 7, 3, 5, 4, None],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 10):
        matchup_matrix = [  # 10 teams, 18 weeks
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],  # week 1
            [9, 8, 7, 6, 10, 4, 3, 2, 1, 5],  # week 2
            [8, 7, 6, 5, 4, 3, 2, 1, 10, 9],  # week 3
            [7, 6, 5, 10, 3, 2, 1, 9, 8, 4],  # week 4
            [6, 5, 4, 3, 2, 1, 9, 10, 7, 8],  # week 5
            [5, 4, 10, 2, 1, 9, 8, 7, 6, 3],  # week 6
            [None, None, None, None, None, None, None, None, None, None],  # week 7
            [4, 3, 2, 1, 9, 8, 10, 6, 5, 7],  # week 8
            [3, 10, 1, 9, 8, 7, 6, 5, 4, 2],  # week 9
            [2, 1, 9, 8, 7, 10, 5, 4, 3, 6],  # week 10
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],  # week 11
            [None, None, None, None, None, None, None, None, None, None],  # week 12
            [9, 8, 7, 6, 10, 4, 3, 2, 1, 5],  # week 13
            [8, 7, 6, 5, 4, 3, 2, 1, 10, 9],  # week 14
            [7, 6, 5, 10, 3, 2, 1, 9, 8, 4],  # week 15
            [6, 5, 4, 3, 2, 1, 9, 10, 7, 8],  # week 16
            [5, 4, 10, 2, 1, 9, 8, 7, 6, 3],  # week 17
            [4, 3, 2, 1, 9, 8, 10, 6, 5, 7],  # week 18
        ]
    elif (flight_db.weeks == 18) and (len(team_ids) == 11):
        matchup_matrix = [  # 11 teams, 18 weeks
            [11, 10, 9, 8, 7, None, 5, 4, 3, 2, 1],  # week 1
            [None, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2],  # week 2
            [2, 1, 11, 10, 9, 8, None, 6, 5, 4, 3],  # week 3
            [3, None, 1, 11, 10, 9, 8, 7, 6, 5, 4],  # week 4
            [4, 3, 2, 1, 11, 10, 9, None, 7, 6, 5],  # week 5
            [5, 4, None, 2, 1, 11, 10, 9, 8, 7, 6],  # week 6
            [6, 5, 4, 3, 2, 1, 11, 10, None, 8, 7],  # week 7
            [7, 6, 5, None, 3, 2, 1, 11, 10, 9, 8],  # week 8
            [8, 7, 6, 5, 4, 3, 2, 1, 11, None, 9],  # week 9
            [9, 8, 7, 6, None, 4, 3, 2, 1, 11, 10],  # week 10
            [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, None],  # week 11
            [11, 10, 9, 8, 7, None, 5, 4, 3, 2, 1],  # week 12
            [None, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2],  # week 13
            [2, 1, 11, None, 9, 8, None, 6, 5, None, 3],  # week 14
            [3, None, 1, 11, 10, 9, 8, 7, 6, 5, 4],  # week 15
            [4, 3, 2, 1, None, 10, 9, None, 7, 6, None],  # week 16
            [5, 4, None, 2, 1, 11, 10, 9, 8, 7, 6],  # week 17
            [6, 5, 4, 3, 2, 1, 11, 10, None, 8, 7],  # week 18
        ]
    else:
        raise ValueError(
            f"No pre-defined {flight_db.weeks}-week matchup matrix for {len(team_ids)} teams"
        )

    # Account for bye week preferences (if possible)
    if bye_weeks_by_team is not None:
        for team_id, bye_week in bye_weeks_by_team.items():
            if team_id not in team_ids:
                raise ValueError(
                    f"Team id '{team_id}' not valid for flight id '{flight_id}'"
                )
            print(f"Team '{team_id}' requested bye week '{bye_week}'")

            team_idx = next(
                idx for idx in range(len(team_ids)) if team_ids[idx] == team_id
            )

            week_matchups = matchup_matrix[bye_week - 1]
            team_idxs_with_bye = [
                idx for idx in range(len(week_matchups)) if week_matchups[idx] is None
            ]

            if len(team_idxs_with_bye) == 0:
                raise ValueError(
                    f"Unable to meet requested bye week for team '{team_id}' - no byes on week '{bye_week}'!"
                )

            if team_idx in team_idxs_with_bye:
                print(f"Team '{team_id}' already has bye on week '{bye_week}'!")
                continue

            # TODO: Improve bye week request clashing checks and multiple bye team options
            # Right now this just forces the first swap!
            old_team_id = team_ids[team_idxs_with_bye[0]]
            team_ids[team_idxs_with_bye[0]] = team_id
            team_ids[team_idx] = old_team_id
            print(
                f"Swapped teams '{team_id}' and '{old_team_id}' to meet bye week '{bye_week}' request"
            )

    # Create matches and add to database
    for week_idx in range(len(matchup_matrix)):
        week = week_idx + 1
        for team_idx in range(len(team_ids)):
            team_id = team_ids[team_idx]
            if matchup_matrix[week_idx][team_idx]:  # check for byes
                opponent_team_id = team_ids[matchup_matrix[week_idx][team_idx] - 1]
                match_db = session.exec(
                    select(Match)
                    .where(Match.flight_id == flight_db.id)
                    .where(Match.week == week)
                    .where(
                        (
                            (Match.home_team_id == team_id)
                            & (Match.away_team_id == opponent_team_id)
                        )
                        | (Match.home_team_id == opponent_team_id)
                        & (Match.away_team_id == team_id)
                    )
                ).one_or_none()
                if not match_db:
                    print(
                        f"Adding match: week={week}, home_team_id={team_id}, away_team_id={opponent_team_id}"
                    )
                    if not dry_run:
                        match_db = Match(
                            flight_id=flight_db.id,
                            week=week,
                            home_team_id=team_id,
                            away_team_id=opponent_team_id,
                        )
                        session.add(match_db)
                        session.commit()

    print(
        f"Completed match initialization for flight: '{flight_db.name} ({flight_db.year})'"
    )
