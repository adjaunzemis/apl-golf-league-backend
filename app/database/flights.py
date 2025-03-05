from sqlmodel import Session, select

from app.models.division import Division
from app.models.flight import Flight, FlightStandings, FlightTeam, FlightTeamGolfer
from app.models.flight_team_link import FlightTeamLink
from app.models.golfer import Golfer
from app.models.match import Match, MatchSummary
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink


def get_teams_in_flight(session: Session, flight_id: int) -> list[FlightTeam]:
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
        if team.id not in teams.keys():
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


def get_flight_match_summaries(session: Session, flight_id: int) -> list[MatchSummary]:
    flight_name = session.exec(select(Flight.name).where(Flight.id == flight_id)).one()
    team_map = {
        team.team_id: team
        for team in get_teams_in_flight(session=session, flight_id=flight_id)
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


def get_standings(id: int) -> FlightStandings:
    pass
