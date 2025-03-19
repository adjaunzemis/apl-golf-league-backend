from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from app.models.course import Course
from app.models.division import Division, FlightDivision
from app.models.flight import (
    Flight,
    FlightInfo,
    FlightStandings,
    FlightStandingsTeam,
    FlightTeam,
    FlightTeamGolfer,
)
from app.models.flight_division_link import FlightDivisionLink
from app.models.flight_team_link import FlightTeamLink
from app.models.golfer import Golfer
from app.models.match import Match, MatchSummary
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink
from app.models.tee import Tee
from app.models.track import Track


def get_ids(session: Session, year: int | None = None) -> list[int]:
    query = select(Flight.id)
    if year:
        query = query.where(Flight.year == year)
    return session.exec(query.order_by(Flight.id)).all()


def get_info(session: Session, flight_id: int) -> FlightInfo:
    flight = session.exec(select(Flight).where(Flight.id == flight_id)).one()
    teams = get_teams(session=session, flight_id=flight_id)
    course = session.exec(
        select(Course).where(Course.id == flight.course_id)
    ).one_or_none()
    return FlightInfo(
        id=flight.id,
        year=flight.year,
        name=flight.name,
        course=course.name if course is not None else None,
        address=course.address if course is not None else None,
        phone=course.phone if course is not None else None,
        logo_url=flight.logo_url,
        secretary=flight.secretary,
        secretary_email=flight.secretary_email,
        signup_start_date=flight.signup_start_date.astimezone()
        .replace(microsecond=0)
        .isoformat(),
        signup_stop_date=flight.signup_stop_date.astimezone()
        .replace(microsecond=0)
        .isoformat(),
        start_date=flight.start_date.astimezone().replace(microsecond=0).isoformat(),
        weeks=flight.weeks,
        tee_times=flight.tee_times,
        num_teams=len(teams),
    )


def get_divisions(session: Session, flight_id: int) -> list[FlightDivision]:
    primary_track = aliased(Track)
    primary_tee = aliased(Tee)
    secondary_track = aliased(Track)
    secondary_tee = aliased(Tee)
    division_query_data = session.exec(
        select(
            Division,
            FlightDivisionLink,
            primary_tee,
            primary_track,
            secondary_tee,
            secondary_track,
        )
        .join(
            FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id
        )
        .join(primary_tee, onclause=Division.primary_tee_id == primary_tee.id)
        .join(primary_track, onclause=primary_tee.track_id == primary_track.id)
        .join(secondary_tee, onclause=Division.secondary_tee_id == secondary_tee.id)
        .join(secondary_track, onclause=secondary_tee.track_id == secondary_track.id)
        .where(FlightDivisionLink.flight_id == flight_id)
    )
    return [
        FlightDivision(
            id=division.id,
            flight_id=flight_division_link.flight_id,
            name=division.name,
            gender=division.gender,
            primary_track_id=primary_track_db.id,
            primary_track_name=primary_track_db.name,
            primary_tee_id=primary_tee_db.id,
            primary_tee_name=primary_tee_db.name,
            primary_tee_par=primary_tee_db.par,
            primary_tee_rating=primary_tee_db.rating,
            primary_tee_slope=primary_tee_db.slope,
            secondary_track_id=secondary_track_db.id,
            secondary_track_name=secondary_track_db.name,
            secondary_tee_id=secondary_tee_db.id,
            secondary_tee_name=secondary_tee_db.name,
            secondary_tee_par=secondary_tee_db.par,
            secondary_tee_rating=secondary_tee_db.rating,
            secondary_tee_slope=secondary_tee_db.slope,
        )
        for division, flight_division_link, primary_tee_db, primary_track_db, secondary_tee_db, secondary_track_db in division_query_data
    ]


def get_teams(session: Session, flight_id: int) -> list[FlightTeam]:
    results = session.exec(
        select(Team, Golfer, TeamGolferLink, Division)
        .join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id)
        .join(TeamGolferLink, onclause=TeamGolferLink.team_id == Team.id)
        .join(Golfer, onclause=Golfer.id == TeamGolferLink.golfer_id)
        .join(Division, onclause=Division.id == TeamGolferLink.division_id)
        .where(FlightTeamLink.flight_id == flight_id)
    ).all()
    teams: dict[int, FlightTeam] = {}

    for team, golfer, teamgolferlink, division in results:
        if team.id not in teams:
            teams[team.id] = FlightTeam(
                flight_id=flight_id, team_id=team.id, name=team.name
            )
        teams[team.id].golfers.append(
            FlightTeamGolfer(
                golfer_id=golfer.id,
                name=golfer.name,
                role=teamgolferlink.role,
                division=division.name,
            )
        )

    for team in teams.values():
        team.golfers.sort(key=lambda g: g.role)

    return list(teams.values())


def get_match_summaries(session: Session, flight_id: int) -> list[MatchSummary]:
    flight_name = session.exec(select(Flight.name).where(Flight.id == flight_id)).one()
    team_map = {
        team.team_id: team for team in get_teams(session=session, flight_id=flight_id)
    }
    matches = session.exec(select(Match).where(Match.flight_id == flight_id)).all()

    match_summaries = [
        MatchSummary(
            match_id=match.id,
            home_team_id=match.home_team_id,
            home_team_name=team_map[match.home_team_id].name,
            away_team_id=match.away_team_id,
            away_team_name=team_map[match.away_team_id].name,
            flight_name=flight_name,
            week=match.week,
            home_score=match.home_score,
            away_score=match.away_score,
        )
        for match in matches
    ]
    match_summaries.sort(key=lambda m: m.week)

    return match_summaries


def get_standings(session: Session, flight_id: int) -> FlightStandings:
    matches = get_match_summaries(session=session, flight_id=flight_id)

    team_data_map: dict[int, FlightStandingsTeam] = {}
    for match in matches:
        if match.home_score is None or match.away_score is None:
            continue

        if match.home_team_id not in team_data_map:
            team_data_map[match.home_team_id] = FlightStandingsTeam(
                team_id=match.home_team_id, team_name=match.home_team_name
            )
        team_data_map[match.home_team_id].matches_played += 1
        team_data_map[match.home_team_id].points_won += match.home_score
        team_data_map[match.home_team_id].avg_points = (
            team_data_map[match.home_team_id].points_won
            / team_data_map[match.home_team_id].matches_played
        )

        if match.away_team_id not in team_data_map:
            team_data_map[match.away_team_id] = FlightStandingsTeam(
                team_id=match.away_team_id, team_name=match.away_team_name
            )
        team_data_map[match.away_team_id].matches_played += 1
        team_data_map[match.away_team_id].points_won += match.away_score
        team_data_map[match.away_team_id].avg_points = (
            team_data_map[match.away_team_id].points_won
            / team_data_map[match.away_team_id].matches_played
        )

    team_data = sorted(team_data_map.values(), key=lambda t: t.avg_points, reverse=True)

    # TODO: Implement tie-breaks

    for idx, team in enumerate(team_data):
        if idx > 0 and team.avg_points == team_data[idx - 1].avg_points:
            team.position = team_data[idx - 1].position
            continue

        if (
            idx < len(team_data) - 1
            and team.avg_points == team_data[idx + 1].avg_points
        ):
            team.position = f"T{idx + 1}"
            continue

        team.position = f"{idx + 1}"

    return FlightStandings(
        flight_id=flight_id,
        teams=team_data,
    )
