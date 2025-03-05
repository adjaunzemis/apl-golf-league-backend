from sqlmodel import Session, select

from app.models.flight import FlightStandings, FlightTeam, FlightTeamGolfer
from app.models.flight_team_link import FlightTeamLink
from app.models.golfer import Golfer
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink


def get_teams_in_flight(session: Session, flight_id: int) -> list[FlightTeam]:
    results = session.exec(
        select(Team, Golfer, TeamGolferLink)
        .join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id)
        .join(TeamGolferLink, onclause=TeamGolferLink.team_id == Team.id)
        .join(Golfer, onclause=Golfer.id == TeamGolferLink.golfer_id)
        .where(FlightTeamLink.flight_id == flight_id)
    ).all()
    teams: dict[int, FlightTeam] = {}
    for team, golfer, teamgolferlink in results:
        if team.id not in teams.keys():
            teams[team.id] = FlightTeam(
                flight_id=flight_id, team_id=team.id, name=team.name
            )
        teams[team.id].golfers.append(
            FlightTeamGolfer(
                golfer_id=golfer.id, name=golfer.name, role=teamgolferlink.role
            )
        )
    return list(teams.values())


def get_flight_matches(session: Session, flight_id: int) -> list:
    pass


def get_standings(id: int) -> FlightStandings:
    pass
