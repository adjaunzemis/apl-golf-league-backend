from sqlmodel import Session, or_, select

from app.models.division import Division
from app.models.golfer import Golfer, GolferTeamData
from app.models.match import Match
from app.models.team import Team
from app.models.team_golfer_link import TeamGolferLink


def get_by_id(session: Session, team_id: int) -> Team | None:
    return session.get(Team, team_id)


def get_golfers(session: Session, team_id: int) -> list[GolferTeamData]:
    results_db = session.exec(
        select(Golfer, TeamGolferLink, Division)
        .join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id)
        .join(Division, onclause=Division.id == TeamGolferLink.division_id)
        .where(TeamGolferLink.team_id == team_id)
    ).all()
    return [
        GolferTeamData(
            golfer_id=golfer_db.id,
            golfer_name=golfer_db.name,
            golfer_role=tgl_db.role,
            division_id=division_db.id,
            division_name=division_db.name,
        )
        for golfer_db, tgl_db, division_db in results_db
    ]


def get_matches(session: Session, team_id: int) -> list[Match]:
    return session.exec(
        select(Match).where(
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id)
        )
    ).all()
