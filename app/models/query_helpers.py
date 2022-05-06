from typing import List, Optional
from datetime import datetime, timedelta
from datetime import date as dt_date
from sqlmodel import Session, select, SQLModel, desc
from sqlalchemy.orm import aliased

from .course import Course
from .track import Track
from .tee import Tee
from .hole import Hole
from .flight import Flight
from .flight_team_link import FlightTeamLink
from .flight_division_link import FlightDivisionLink
from .tournament_round_link import TournamentRoundLink
from .tournament_team_link import TournamentTeamLink
from .tournament_division_link import TournamentDivisionLink
from .tournament import Tournament
from .team import Team, TeamRead
from .team_golfer_link import TeamGolferLink
from .golfer import Golfer, GolferStatistics
from .division import Division, DivisionData
from .match import Match, MatchData, MatchSummary
from .round import Round, RoundData, RoundSummary, ScoringType
from .hole_result import HoleResult, HoleResultData
from .match_round_link import MatchRoundLink
from .round_golfer_link import RoundGolferLink
from .qualifying_score import QualifyingScore

from ..utilities.world_handicap_system import WorldHandicapSystem
from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem
from ..utilities.apl_handicap_system import APLHandicapSystem

# TODO: Move custom route data models elsewhere
class HandicapIndexData(SQLModel):
    active_date: str
    active_handicap_index: float = None
    active_rounds: Optional[List[RoundSummary]] = None
    pending_handicap_index: Optional[float] = None
    pending_rounds: Optional[List[RoundSummary]] = None

class GolferTeamData(SQLModel):
    team_id: int
    golfer_id: int
    golfer_name: str
    golfer_email: Optional[str] = None
    division_name: str
    flight_id: Optional[int] = None
    flight_name: Optional[str] = None
    tournament_id: Optional[int] = None
    tournament_name: Optional[str] = None
    team_name: str
    role: str
    year: int
    statistics: Optional[GolferStatistics] = None
    handicap_index: Optional[float] = None
    handicap_index_updated: Optional[str] = None

class GolferData(SQLModel):
    golfer_id: int
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    member_since: int = None
    handicap_index_data: HandicapIndexData = None

class GolferDataWithCount(SQLModel):
    num_golfers: int
    golfers: List[GolferData]
    
class TeamWithMatchData(SQLModel):
    id: int
    name: str
    year: int
    golfers: List[GolferTeamData] = []
    matches: List[MatchData] = []

class FlightTeamReadWithGolfers(TeamRead):
    flight_id: int
    golfers: List[GolferTeamData]

class TournamentTeamData(TeamRead):
    id: int
    name: str
    year: int
    tournament_id: int
    golfers: List[GolferTeamData]
    rounds: Optional[List[RoundData]] = []

class FlightInfo(SQLModel):
    id: int
    year: int
    name: str
    course: str = None
    logo_url: str = None
    secretary: str = None
    secretary_email: str = None
    signup_start_date: str = None
    signup_stop_date: str = None
    start_date: str = None
    weeks: int = None

class FlightData(SQLModel):
    id: int
    year: int
    name: str
    course: str = None
    logo_url: str = None
    secretary: str = None
    secretary_email: str = None
    secretary_phone: str = None
    signup_start_date: str = None
    signup_stop_date: str = None
    start_date: str = None
    weeks: int = None
    locked: bool = False
    divisions: List[DivisionData] = []
    teams: List[FlightTeamReadWithGolfers] = []
    matches: List[MatchSummary] = []
    
class FlightInfoWithCount(SQLModel):
    num_flights: int
    flights: List[FlightInfo]

class TournamentInfo(SQLModel):
    id: int
    year: int
    name: str
    date: str = None
    course: str = None
    logo_url: str = None
    secretary: str = None
    secretary_email: str = None
    signup_start_date: str = None
    signup_stop_date: str = None
    members_entry_fee: float = None
    non_members_entry_fee: float = None
    shotgun: bool = False
    strokeplay: bool = False
    bestball: bool = False
    scramble: bool = False
    ryder_cup: bool = False
    individual: bool = False
    chachacha: bool = False

class TournamentData(SQLModel):
    id: int
    year: int
    name: str
    date: str = None
    course: str = None
    logo_url: str = None
    secretary: str = None
    secretary_email: str = None
    secretary_phone: str = None
    signup_start_date: str = None
    signup_stop_date: str = None
    members_entry_fee: float = None
    non_members_entry_fee: float = None
    locked: bool = False
    divisions: List[DivisionData] = []
    teams: List[TournamentTeamData] = []
    shotgun: bool = False
    strokeplay: bool = False
    bestball: bool = False
    scramble: bool = False
    ryder_cup: bool = False
    individual: bool = False
    chachacha: bool = False

class TournamentInfoWithCount(SQLModel):
    num_tournaments: int
    tournaments: List[TournamentInfo]

def get_flights(session: Session, flight_ids: List[int]) -> List[FlightData]:
    """
    Retrieves flight data from database.

    Parameters
    ----------
    session : Session
        database session
    flight_ids : list of integers
        flight identifiers
    
    Returns
    -------
    flight_data : list of FlightData
        flight data from database
    
    """
    # flight_query_data = session.exec(select(Flight, Course).join(Course).where(Flight.id.in_(flight_ids)).order_by(Flight.year))
    flights_db = session.exec(select(Flight).where(Flight.id.in_(flight_ids)).order_by(Flight.year)).all()
    courses_db = session.exec(select(Course).where(Course.id.in_([flight_db.course_id for flight_db in flights_db]))).all()
    flight_courses_db: List[Course] = []
    for flight_db in flights_db:
        flight_courses_db.append([course_db for course_db in courses_db if course_db.id == flight_db.course_id][0] if flight_db.course_id else None)
    return [FlightData(
        id=flight.id,
        year=flight.year,
        name=flight.name,
        logo_url=flight.logo_url,
        secretary=flight.secretary,
        secretary_email=flight.secretary_email,
        secretary_phone=flight.secretary_phone,
        signup_start_date=flight.signup_start_date.astimezone().replace(microsecond=0).isoformat() if flight.signup_start_date else None,
        signup_stop_date=flight.signup_stop_date.astimezone().replace(microsecond=0).isoformat() if flight.signup_stop_date else None,
        start_date=flight.start_date.astimezone().replace(microsecond=0).isoformat() if flight.start_date else None,
        weeks=flight.weeks,
        locked=flight.locked,
        course=flight_courses_db[idx].name if flight_courses_db[idx] else None
    ) for idx, flight in enumerate(flights_db)]

def get_tournaments(session: Session, tournament_ids: List[int]) -> List[TournamentData]:
    """
    Retrieves tournament data from database.

    Parameters
    ----------
    session : Session
        database session
    tournament_ids : list of integers
        tournament identifiers
    
    Returns
    -------
    tournament_data : list of TournamentData
        tournament data from database
    
    """
    tournament_query_data = session.exec(select(Tournament, Course).join(Course).where(Tournament.id.in_(tournament_ids)).order_by(Tournament.date))
    return [TournamentData(
        id=tournament.id,
        year=tournament.year,
        name=tournament.name,
        date=tournament.date.astimezone().replace(microsecond=0).isoformat() if tournament.date else None,
        logo_url=tournament.logo_url,
        secretary=tournament.secretary,
        secretary_email=tournament.secretary_email,
        secretary_phone=tournament.secretary_phone,
        signup_start_date=tournament.signup_start_date.astimezone().replace(microsecond=0).isoformat() if tournament.signup_start_date else None,
        signup_stop_date=tournament.signup_stop_date.astimezone().replace(microsecond=0).isoformat() if tournament.signup_stop_date else None,
        members_entry_fee=tournament.members_entry_fee,
        non_members_entry_fee=tournament.non_members_entry_fee,
        course=course.name,
        locked=tournament.locked,
        shotgun=tournament.shotgun,
        strokeplay=tournament.strokeplay,
        bestball=tournament.bestball,
        scramble=tournament.scramble,
        ryder_cup=tournament.ryder_cup,
        individual=tournament.individual,
        chachacha=tournament.chachacha
    ) for tournament, course in tournament_query_data]

def get_divisions_in_flights(session: Session, flight_ids: List[int]) -> List[DivisionData]:
    """
    Retrieves division data for all divisions in the given flights.
    
    Parameters
    ----------
    session : Session
        database session
    flight_ids : list of integers
        flight identifiers
    
    Returns
    -------
    division_data : list of DivisionData
        division data for division in the given flights
         
    """
    primary_track = aliased(Track)
    primary_tee = aliased(Tee)
    secondary_track = aliased(Track)
    secondary_tee = aliased(Tee)
    division_query_data = session.exec(select(Division, FlightDivisionLink, primary_tee, primary_track, secondary_tee, secondary_track).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(primary_tee, onclause=Division.primary_tee_id == primary_tee.id).join(primary_track, onclause=primary_tee.track_id == primary_track.id).join(secondary_tee, onclause=Division.secondary_tee_id == secondary_tee.id).join(secondary_track, onclause=secondary_tee.track_id == secondary_track.id).where(FlightDivisionLink.flight_id.in_(flight_ids)))
    return [DivisionData(
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
        secondary_tee_slope=secondary_tee_db.slope
    ) for division, flight_division_link, primary_tee_db, primary_track_db, secondary_tee_db, secondary_track_db in division_query_data]

def get_divisions_in_tournaments(session: Session, tournament_ids: List[int]) -> List[DivisionData]:
    """
    Retrieves division data for all teams in the given tournaments.

    Parameters
    ----------
    session : Session
        database session
    tournament_ids : list of integers
        tournament identifiers
    
    Returns
    -------
    division_data : list of DivisionData
        division data for division in the given tournaments

    """
    primary_track = aliased(Track)
    primary_tee = aliased(Tee)
    secondary_track = aliased(Track)
    secondary_tee = aliased(Tee)
    division_query_data = session.exec(select(Division, TournamentDivisionLink, primary_tee, primary_track, secondary_tee, secondary_track).join(TournamentDivisionLink, onclause=TournamentDivisionLink.division_id == Division.id).join(primary_tee, onclause=Division.primary_tee_id == primary_tee.id).join(primary_track, onclause=primary_tee.track_id == primary_track.id).join(secondary_tee, onclause=Division.secondary_tee_id == secondary_tee.id).join(secondary_track, onclause=secondary_tee.track_id == secondary_track.id).where(TournamentDivisionLink.tournament_id.in_(tournament_ids)))
    return [DivisionData(
        id=division.id,
        tournament_id=tournament_division_link.tournament_id,
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
        secondary_tee_slope=secondary_tee_db.slope
    ) for division, tournament_division_link, primary_tee_db, primary_track_db, secondary_tee_db, secondary_track_db in division_query_data]

def get_teams_in_flights(session: Session, flight_ids: List[int]) -> List[FlightTeamReadWithGolfers]:
    """
    Retrieves team data for all teams in the given flights.
    
    Parameters
    ----------
    session : Session
        database session
    flight_ids : list of integers
        flight identifiers
    
    Returns
    -------
    team_data : list of TeamReadWithData
        teams in the given flights
    
    """
    team_query_data = session.exec(select(Team.id, Team.name, Flight).join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id).join(Flight, onclause=Flight.id == FlightTeamLink.flight_id).where(Flight.id.in_(flight_ids))).all()
    team_golfers = get_flight_team_golfers_for_teams(session=session, team_ids=(team_id for team_id, team_name, flight in team_query_data))
    return [FlightTeamReadWithGolfers(id=team_id, flight_id=flight.id, name=team_name, golfers=[golfer for golfer in team_golfers if golfer.team_id == team_id]) for team_id, team_name, flight in team_query_data]

def get_teams_in_tournaments(session: Session, tournament_ids: List[int]) -> List[TournamentTeamData]:
    """
    Retrieves team data for all teams in the given tournaments.
    
    Parameters
    ----------
    session : Session
        database session
    tournament_ids : list of integers
        tournament identifiers
    
    Returns
    -------
    team_data : list of TournamentTeamReadWithGolfers
        teams in the given tournaments
    
    """
    team_query_data = session.exec(select(Team.id, Team.name, Tournament).join(TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id).join(Tournament, onclause=Tournament.id == TournamentTeamLink.tournament_id).where(Tournament.id.in_(tournament_ids))).all()
    team_golfers = get_tournament_team_golfers_for_teams(session=session, team_ids=(team_id for team_id, team_name, tournament in team_query_data))
    return [TournamentTeamData(id=team_id, tournament_id=tournament.id, name=team_name, year=tournament.year, golfers=[golfer for golfer in team_golfers if golfer.team_id == team_id]) for team_id, team_name, tournament in team_query_data]

def get_golfers(session: Session, golfer_ids: List[int], min_date: dt_date = datetime(datetime.today().year - 2, 1, 1).date(), max_date: dt_date = datetime.today().date() + timedelta(days=1), include_scoring_record: bool = False, use_legacy_handicapping: bool = False) -> List[GolferData]:
    """
    Retrieves golfer data for the given golfers.
    
    Parameters
    ----------
    session : Session
        database session
    golfer_ids : list of integers
        golfer identifiers
    min_date: date, optional
        minimum date for handicap index calculation
    max_date: date, optional
        maximum date for active handicap index calculation
        Default: tomorrow's date (includes all rounds through current day in active index)
    include_scoring_record : boolean, optional
        if true, includes scoring record rounds with handicap index data
        Default: False
    use_legacy_handicapping : boolean, optional
        if true, uses APL legacy handicapping system
        Default: False
        
    Returns
    -------
    golfer_data : list of GolferData
        golfer data for the given golfers

    """
    golfer_query_data = session.exec(select(Golfer).where(Golfer.id.in_(golfer_ids)))
    golfer_data = [GolferData(
        golfer_id=golfer.id,
        name=golfer.name,
        email=golfer.email,
        phone=golfer.phone,
        affiliation=golfer.affiliation,
        member_since=get_golfer_year_joined(session=session, golfer_id=golfer.id),
        handicap_index_data=get_handicap_index_data(session=session, golfer_id=golfer.id, min_date=min_date, max_date=max_date, limit=10, include_rounds=include_scoring_record, use_legacy_handicapping=use_legacy_handicapping)
    ) for golfer in golfer_query_data]
    return golfer_data

def get_golfer_team_data(session: Session, golfer_ids: List[int], year: int = None) -> List[GolferTeamData]:
    """
    Retrieves team golfer data for the given golfers.
    
    Parameters
    ----------
    session : Session
        database session
    golfer_ids : list of integers
        golfer identifiers
    year : integer, optional
        filters results to teams during the given season
        Default: None (no year filtering)

    Returns
    -------
    golfer_team_data : list of TeamGolferData
        team data for the given golfers

    """
    if year: # filter results by year
        flight_team_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Flight).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(Flight, onclause=FlightDivisionLink.flight_id == Flight.id).where(Flight.year == year).where(TeamGolferLink.golfer_id.in_(golfer_ids))).all()
        tournament_team_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Tournament).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(TournamentDivisionLink, onclause=TournamentDivisionLink.division_id == Division.id).join(Tournament, onclause=TournamentDivisionLink.tournament_id == Tournament.id).where(Tournament.year == year).where(TeamGolferLink.golfer_id.in_(golfer_ids))).all()
    else: # no filtering
        flight_team_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Flight).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(Flight, onclause=FlightDivisionLink.flight_id == Flight.id).where(TeamGolferLink.golfer_id.in_(golfer_ids))).all()
        tournament_team_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Tournament).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(TournamentDivisionLink, onclause=TournamentDivisionLink.division_id == Division.id).join(Tournament, onclause=TournamentDivisionLink.tournament_id == Tournament.id).where(TeamGolferLink.golfer_id.in_(golfer_ids))).all()
    golfer_team_data = [GolferTeamData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        golfer_email=golfer.email,
        flight_id=flight.id,
        flight_name=flight.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role,
        year=flight.year,
        handicap_index=golfer.handicap_index,
        handicap_index_updated=golfer.handicap_index_updated.astimezone().replace(microsecond=0).isoformat() if golfer.handicap_index_updated else None
    ) for team_golfer_link, team, golfer, division, flight in flight_team_data]
    golfer_team_data.extend([GolferTeamData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        golfer_email=golfer.email,
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role,
        year=tournament.year,
        handicap_index=golfer.handicap_index,
        handicap_index_updated=golfer.handicap_index_updated.astimezone().replace(microsecond=0).isoformat() if golfer.handicap_index_updated else None
    ) for team_golfer_link, team, golfer, division, tournament in tournament_team_data])
    return golfer_team_data

def get_flight_team_golfers_for_teams(session: Session, team_ids: List[int]) -> List[GolferTeamData]:
    """
    Retrieves team golfer data for the given teams.

    Parameters
    ----------
    session : Session
        database session
    team_ids : list of integers
        team identifiers

    Returns
    -------
    team_golfer_data : list of TeamGolferData
        team golfer data for golfers on the given teams
    
    """
    query_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Flight).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(Flight, onclause=FlightDivisionLink.flight_id == Flight.id).where(TeamGolferLink.team_id.in_(team_ids)))
    return [GolferTeamData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        golfer_email=golfer.email,
        flight_id=flight.id,
        flight_name=flight.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role,
        year=flight.year,
        handicap_index=golfer.handicap_index,
        handicap_index_updated=golfer.handicap_index_updated.astimezone().replace(microsecond=0).isoformat() if golfer.handicap_index_updated else None
    ) for team_golfer_link, team, golfer, division, flight in query_data]

def get_tournament_team_golfers_for_teams(session: Session, team_ids: List[int]) -> List[GolferTeamData]:
    """
    Retrieves team golfer data for the given teams.

    TODO: Conslidate with `get_flight_team_golfers_for_teams()`

    Parameters
    ----------
    session : Session
        database session
    team_ids : list of integers
        team identifiers

    Returns
    -------
    team_golfer_data : list of TeamGolferData
        team golfer data for golfers on the given teams
    
    """
    query_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Tournament).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(TournamentDivisionLink, onclause=TournamentDivisionLink.division_id == Division.id).join(Tournament, onclause=TournamentDivisionLink.tournament_id == Tournament.id).where(TeamGolferLink.team_id.in_(team_ids)))
    return [GolferTeamData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        golfer_email=golfer.email,
        tournament_id=tournament.id,
        tournament_name=tournament.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role,
        year=tournament.year,
        handicap_index=golfer.handicap_index,
        handicap_index_updated=golfer.handicap_index_updated.astimezone().replace(microsecond=0).isoformat() if golfer.handicap_index_updated else None
    ) for team_golfer_link, team, golfer, division, tournament in query_data]

def get_matches(session: Session, match_ids: List[int]) -> List[MatchData]:
    """
    Retrieves match data for the given matches, including round results.

    Parameters
    ----------
    session : Session
        database session
    match_ids : list of integers
        match identifiers

    Returns
    -------
    match_data : list of MatchData
        match data for the given matches, sorted by week
    
    """
    home_team = aliased(Team)
    away_team = aliased(Team)
    match_query_data = session.exec(select(Match, Flight, home_team, away_team).join(Flight, onclause=Match.flight_id == Flight.id).join(home_team, onclause=Match.home_team_id == home_team.id).join(away_team, onclause=Match.away_team_id == away_team.id).where(Match.id.in_(match_ids))).all()
    match_data = [MatchData(
        match_id=match.id,
        home_team_id=match.home_team_id,
        home_team_name=home_team.name,
        away_team_id=match.away_team_id,
        away_team_name=away_team.name,
        flight_name=flight.name,
        week=match.week,
        home_score=match.home_score,
        away_score=match.away_score
    ) for match, flight, home_team, away_team in match_query_data]

    # Sort matches by week
    match_data.sort(key=lambda m: m.week)
    
    # Get round data for selected matches
    round_data = get_rounds_for_matches(session=session, match_ids=[m.match_id for m in match_data])

    # Add round data to match data and return
    for m in match_data:
        m.rounds = [r for r in round_data if r.match_id == m.match_id]
    return match_data

def get_matches_for_teams(session: Session, team_ids: List[int]) -> List[MatchData]:
    """
    Retrieves match data for the given teams.

    Parameters
    ----------
    session : Session
        database session
    team_ids : list of integers
        team identifiers

    Returns
    -------
    match_data : list of MatchData
        matches played by the given teams
    
    """
    match_ids = session.exec(select(Match.id).where((Match.home_team_id.in_(team_ids)) | (Match.away_team_id.in_(team_ids)))).all()
    return get_matches(session=session, match_ids=match_ids)

def get_flight_rounds(session: Session, round_ids: List[int]) -> List[RoundData]:
    """
    Retrieves round data for the given flight-play rounds, including results.

    Parameters
    ----------
    session : Session
        database session
    round_ids : list of integers
        round identifiers
    
    Returns
    -------
    round_data : list of RoundData
        round data for the given rounds
    
    """
    round_query_data = session.exec(select(Round, MatchRoundLink, RoundGolferLink, Golfer, Course, Track, Tee, Team).join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).join(Tee).join(Track).join(Course).join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id).join(Match, onclause=Match.id == MatchRoundLink.match_id).join(TeamGolferLink, ((TeamGolferLink.golfer_id == Golfer.id) & (TeamGolferLink.team_id.in_((Match.home_team_id, Match.away_team_id))))).join(Team, onclause=Team.id == TeamGolferLink.team_id).where(Round.id.in_(round_ids)))
    round_data = [RoundData(
        round_id=round.id,
        match_id=match_round_link.match_id,
        team_id=team.id,
        round_type=round.type,
        date_played=round.date_played,
        date_updated=round.date_updated,
        golfer_id=round_golfer_link.golfer_id,
        golfer_name=golfer.name,
        golfer_playing_handicap=round_golfer_link.playing_handicap,
        team_name=team.name,
        course_id=course.id,
        course_name=course.name,
        track_id=track.id,
        track_name=track.name,
        tee_id=tee.id,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_par=tee.par,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, match_round_link, round_golfer_link, golfer, course, track, tee, team in round_query_data]

    # Query hole data for selected rounds
    hole_result_data = get_hole_results_for_rounds(session=session, round_ids=[r.round_id for r in round_data])

    # Add hole data to round data and return
    ahs = APLLegacyHandicapSystem()
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])
        r.score_differential = ahs.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score)
    return round_data

def get_rounds_for_matches(session: Session, match_ids: List[int]) -> List[RoundData]:
    """
    Retrieves round data for the given matches.

    Parameters
    ----------
    session : Session
        database session
    match_ids : list of integers
        match identifiers
    
    Returns
    -------
    round_data : list of RoundData
        rounds played for the given matches
    
    """
    round_ids = session.exec(select(Round.id).join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id).where(MatchRoundLink.match_id.in_(match_ids))).all()
    return get_flight_rounds(session=session, round_ids=round_ids)

def get_rounds_for_tournament(session: Session, tournament_id: int) -> List[RoundData]:
    """
    Retrieves round data for the given tournament.

    Parameters
    ----------
    session : Session
        database session
    tournament_id : integer
        tournament identifier
    
    Returns
    -------
    round_data : list of RoundData
        rounds played for the given tournament

    """
    round_ids = session.exec(select(Round.id).join(TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id).where(TournamentRoundLink.tournament_id == tournament_id)).all()
    return get_tournament_rounds(session=session, tournament_id=tournament_id, round_ids=round_ids)

def get_tournament_rounds(session: Session, tournament_id: int, round_ids: List[int]) -> List[RoundData]:
    """
    Retrieves round data for the given tournament-play rounds, including results.

    Parameters
    ----------
    session : Session
        database session
    tournament_id : integer
        tournament identifier
    round_ids : list of integers
        round identifiers
    
    Returns
    -------
    round_data : list of RoundData
        round data for the given rounds
    
    """
    round_query_data = session.exec(select(Round, RoundGolferLink, Golfer, Team, Course, Track, Tee).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id).join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Team, onclause=Team.id == TeamGolferLink.team_id).join(TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id).join(TournamentRoundLink, onclause=TournamentRoundLink.round_id == Round.id).join(Tee).join(Track).join(Course).where(Round.id.in_(round_ids)).where(TournamentTeamLink.tournament_id == tournament_id)).all()
    round_data = [RoundData(
        round_id=round.id,
        match_id=None, # TODO: remove match_id from RoundData
        team_id=team.id,
        round_type=round.type,
        date_played=round.date_played,
        date_updated=round.date_updated,
        golfer_id=round_golfer_link.golfer_id,
        golfer_name=golfer.name,
        golfer_playing_handicap=round_golfer_link.playing_handicap,
        team_name=team.name,
        course_id=course.id,
        course_name=course.name,
        track_id=track.id,
        track_name=track.name,
        tee_id=tee.id,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_par=tee.par,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, round_golfer_link, golfer, team, course, track, tee in round_query_data]

    # Query hole data for selected rounds
    hole_result_data = get_hole_results_for_rounds(session=session, round_ids=[r.round_id for r in round_data])

    # Add hole data to round data and return
    ahs = APLLegacyHandicapSystem()
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])
        r.score_differential = ahs.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score)
    return round_data

def get_hole_results_for_rounds(session: Session, round_ids: List[int]) -> List[HoleResultData]:
    """
    Retrieves hole result data for the given rounds.

    Parameters
    ----------
    session : Session
        database session
    round_ids : list of integers
        round identifiers
    
    Returns
    -------
    hole_result_data : list of HoleResultData
        hole results for the given rounds

    """
    # TODO: Simplify using HoleResultRead* classes
    hole_query_data = session.exec(select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_(round_ids)))
    return [HoleResultData(
        hole_result_id=hole_result.id,
        round_id=hole_result.round_id,
        hole_id=hole_result.hole_id,
        number=hole.number,
        par=hole.par,
        yardage=hole.yardage,
        stroke_index=hole.stroke_index,
        handicap_strokes=hole_result.handicap_strokes,
        gross_score=hole_result.gross_score,
        adjusted_gross_score=hole_result.adjusted_gross_score,
        net_score=hole_result.net_score
    ) for hole_result, hole in hole_query_data]

def compute_golfer_statistics_for_rounds(golfer_id: int, rounds: List[RoundData]) -> GolferStatistics:
    """
    Computes statistics for the given golfer from the given rounds.

    Filters rounds by golfer_id before processing statistics.

    Parameters
    ----------
    golfer_id : int
        golfer identifier
    rounds : list of RoundData
        rounds to process for statistics

    Returns
    -------
    stats : GolferStatistics
        statistics computed from rounds for the given golfer
    
    """
    stats = GolferStatistics()
    for round in rounds:
        if round.golfer_id == golfer_id:
            stats.num_rounds += 1
            stats.num_holes += len(round.holes)
            stats.avg_gross_score += ((round.gross_score - stats.avg_gross_score) / stats.num_rounds)
            stats.avg_net_score += ((round.net_score - stats.avg_net_score) / stats.num_rounds)
            for hole in round.holes:
                if hole.gross_score == 1:
                    stats.num_aces += 1
                elif hole.gross_score == (hole.par - 3):
                    stats.num_albatrosses += 1
                elif hole.gross_score == (hole.par - 2):
                    stats.num_eagles += 1
                elif hole.gross_score == (hole.par - 1):
                    stats.num_birdies += 1
                elif hole.gross_score == hole.par:
                    stats.num_pars += 1
                elif hole.gross_score == (hole.par + 1):
                    stats.num_bogeys += 1
                elif hole.gross_score == (hole.par + 2):
                    stats.num_double_bogeys += 1
                elif hole.gross_score > (hole.par + 2):
                    stats.num_others += 1
    return stats

def compute_golfer_statistics_for_matches(golfer_id: int, matches: List[MatchData]) -> GolferStatistics:
    """
    Extracts rounds for given golfer from given matches, computes statistics.

    Filters rounds by golfer_id before processing statistics.
    
    Parameters
    ----------
    golfer_id : int
        golfer identifier in database
    matches : list of MatchData
        matches containing rounds to analyze
    
    Returns
    -------
    stats : GolferStatistics
        statistics computed from rounds for the given golfer
        
    """
    rounds = []
    for match in matches:
        rounds.extend([round for round in match.rounds if round.golfer_id == golfer_id])
    return compute_golfer_statistics_for_rounds(golfer_id, rounds)

def get_round_summaries(session: Session, round_ids: List[int], use_legacy_handicapping: bool = False) -> List[RoundSummary]:
    """
    """
    if use_legacy_handicapping:
        handicap_system = APLLegacyHandicapSystem()
    else:
        handicap_system = APLHandicapSystem()

    round_query_data = session.exec(select(Round, RoundGolferLink, Golfer, Course, Track, Tee).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id).join(Tee).join(Track).join(Course).where(Round.id.in_(round_ids))).all()
    round_summaries = [RoundSummary(
        round_id=round.id,
        date_played=round.date_played,
        round_type=round.type,
        golfer_name=golfer.name,
        golfer_playing_handicap=round_golfer_link.playing_handicap,
        course_name=course.name,
        track_name=track.name,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_par=tee.par,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, round_golfer_link, golfer, course, track, tee in round_query_data]
    
    # Query hole data for selected rounds
    hole_result_data = get_hole_results_for_rounds(session=session, round_ids=round_ids)

    # Add hole data to round data and return
    for r in round_summaries:
        round_holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in round_holes])
        r.gross_score = sum([h.gross_score for h in round_holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in round_holes])
        r.net_score = sum([h.net_score for h in round_holes])
        r.score_differential = handicap_system.compute_score_differential(r.tee_rating, r.tee_slope, r.adjusted_gross_score)
    return round_summaries

def get_rounds_in_scoring_record(session: Session, golfer_id: int, min_date: dt_date, max_date: dt_date, limit: int = 20, use_legacy_handicapping: bool = False) -> List[RoundSummary]:
    """
    Extracts round data for rounds in golfer's scoring record.

    Scoring record is used for calculating handicap index and includes the
    golfer's most recent rounds as of the given date.

    Parameters
    ----------
    session : Session
        database session
    golfer_id : int
        golfer identifier in database
    min_date: date
        earliest date allowed for rounds in this scoring record
    max_date : date
        latest date allowed for rounds in this scoring record
    limit : int, optional
        maximum rounds allowed in scoring record
        Default: 20
    use_legacy_handicapping : boolean, optional
        if true, uses APL legacy handicapping system
        Default: False
    
    Returns
    -------
    rounds : list of RoundData
        round data for rounds in golfer's scoring record
    
    """
    round_ids = session.exec(select(Round.id).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).where(RoundGolferLink.golfer_id == golfer_id).where(Round.scoring_type == ScoringType.INDIVIDUAL).where(Round.date_played >= min_date).where(Round.date_played <= max_date).order_by(desc(Round.date_played)).limit(limit)).all()
    round_summaries = get_round_summaries(session=session, round_ids=round_ids, use_legacy_handicapping=use_legacy_handicapping)
    if len(round_summaries) < 2: # include qualifying scores
        qualifying_scores_db = session.exec(select(QualifyingScore).where(QualifyingScore.golfer_id == golfer_id).where(QualifyingScore.date_played >= min_date).where(QualifyingScore.date_played <= max_date)).all()
        for qualifying_score_db in qualifying_scores_db:
            round_summaries.append(RoundSummary(
                date_played=qualifying_score_db.date_played,
                date_updated=qualifying_score_db.date_updated,
                course_name=f"Qualifying Score: {qualifying_score_db.course_name if qualifying_score_db.course_name is not None else qualifying_score_db.type}",
                track_name=qualifying_score_db.track_name if qualifying_score_db.track_name is not None else None,
                tee_name=qualifying_score_db.tee_name if qualifying_score_db.tee_name is not None else None,
                tee_gender=qualifying_score_db.tee_gender if qualifying_score_db.tee_gender is not None else None,
                tee_par=qualifying_score_db.tee_par if qualifying_score_db.tee_par is not None else None,
                tee_rating=qualifying_score_db.tee_rating if qualifying_score_db.tee_rating is not None else None,
                tee_slope=qualifying_score_db.tee_slope if qualifying_score_db.tee_slope is not None else None,
                gross_score=qualifying_score_db.gross_score if qualifying_score_db.gross_score is not None else None,
                adjusted_gross_score=qualifying_score_db.adjusted_gross_score if qualifying_score_db.adjusted_gross_score is not None else None,
                score_differential=qualifying_score_db.score_differential
            ))
    return sorted(round_summaries, key=lambda round_summary: round_summary.date_played, reverse=True)

def get_handicap_index_data(session: Session, golfer_id: int, min_date: dt_date, max_date: dt_date, limit: int = 20, include_rounds: bool = False, use_legacy_handicapping: bool = False) -> HandicapIndexData:
    """
    Extracts round data for golfer's scoring record and computes handicap index.

    Parameters
    ----------
    session : Session
        database session
    golfer_id : int
        golfer identifier in database
    min_date : date
        earliest date allowed for rounds in the scoring record
    max_date : date
        latest date allowed for rounds in the scoring record
        Note: rounds after this date will be in the "pending" scoring record
    limit : int, optional
        maximum rounds allowed in scoring record
        Default: 20
    include_record : boolean, optional
        if true, includes rounds in scoring records with result
        Default: False
    use_legacy_handicapping : boolean, optional
        if true, uses APL legacy handicapping system
        Default: False

    Returns
    -------
    data : HandicapIndexData
        computed handicap index and supporting data if requested
    
    """
    if use_legacy_handicapping:
        handicap_system = APLLegacyHandicapSystem()
    else:
        handicap_system = APLHandicapSystem()
    # Process active scoring record (between min_date and max_date)
    active_index = None
    active_rounds = get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, min_date=min_date, max_date=max_date, limit=limit, use_legacy_handicapping=use_legacy_handicapping)
    active_record = [r.score_differential for r in active_rounds]
    if len(active_record) > 0:
        active_index = handicap_system.compute_handicap_index(record=active_record)
    # Process pending scoring record (between max_date and now)
    pending_rounds = []
    pending_index = None
    if (datetime.today().date() > max_date):
        pending_rounds = get_rounds_in_scoring_record(session=session, golfer_id=golfer_id, min_date=max_date, max_date=datetime.today() + timedelta(days=1), limit=limit, use_legacy_handicapping=use_legacy_handicapping)
        pending_record = [r.score_differential for r in pending_rounds]
        if len(pending_record) > 0:
            if len(pending_record) < limit:
                pending_record = pending_record + active_record
                if len(pending_record) > limit:
                    pending_record = pending_record[:limit]
            pending_index = handicap_system.compute_handicap_index(record=pending_record)
    # Return results
    data = HandicapIndexData(
        active_date=datetime.combine(max_date, datetime.min.time()).astimezone().replace(microsecond=0).isoformat(),
        active_handicap_index=active_index,
        pending_handicap_index=pending_index,
        active_rounds=None,
        pending_rounds=None
    )
    if include_rounds:
        data.active_rounds = active_rounds
        data.pending_rounds = pending_rounds
    return data

def get_golfer_year_joined(session: Session, golfer_id: int) -> int:
    """
    Determines year golfer joined league based on oldest round in database.

    Parameters
    ----------
    session : Session
        database session
    golfer_id : integer
        golfer identifier
    
    Returns
    -------
    year_joined : date
        year of golfer's oldest round, or None if no rounds found
    
    """
    oldest_round_date = session.exec(select(Round.date_played).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).where(RoundGolferLink.golfer_id == golfer_id).order_by(Round.date_played).limit(1)).one_or_none()
    if not oldest_round_date:
        return None
    return oldest_round_date.year
