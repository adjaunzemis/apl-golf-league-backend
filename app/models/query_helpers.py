from typing import List
from datetime import date
from sqlmodel import Session, select, SQLModel, desc
from sqlalchemy.orm import aliased
from app.models.tournament import Tournament

from app.models.tournament_team_link import TournamentTeamLink

from .course import Course
from .track import Track
from .tee import Tee
from .hole import Hole
from .flight import Flight
from .flight_team_link import FlightTeamLink
from .flight_division_link import FlightDivisionLink
from .team import Team, FlightTeamReadWithGolfers, TournamentTeamData
from .golfer import Golfer, GolferStatistics
from .division import Division, FlightDivisionData, TournamentDivisionData
from .match import Match, MatchData, MatchSummary
from .round import Round, RoundData
from .hole_result import HoleResult, HoleResultData
from .round_golfer_link import RoundGolferLink
from .match_round_link import MatchRoundLink
from .team_golfer_link import TeamGolferLink
from .tournament_division_link import TournamentDivisionLink

from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

# TODO: Move custom route data models elsewhere
class TeamGolferData(SQLModel):
    team_id: int
    golfer_id: int
    golfer_name: str
    division_name: str
    flight_name: str
    team_name: str
    role: str
    statistics: GolferStatistics = None

class GolferData(SQLModel):
    golfer_id: int
    name: str
    affiliation: str
    team_golfer_data: List[TeamGolferData] = []

class GolferDataWithCount(SQLModel):
    num_golfers: int
    golfers: List[GolferData]
    
class TeamWithMatchData(SQLModel):
    team_id: int
    name: str
    golfers: List[TeamGolferData] = []
    matches: List[MatchData] = []
    
class FlightData(SQLModel):
    flight_id: int
    year: int
    name: str
    logo_url: str = None
    secretary: str = None
    secretary_contact: str = None
    home_course_name: str = None
    divisions: List[FlightDivisionData] = []
    teams: List[FlightTeamReadWithGolfers] = []
    matches: List[MatchSummary] = []
    
class FlightDataWithCount(SQLModel):
    num_flights: int
    flights: List[FlightData]

class TournamentData(SQLModel):
    tournament_id: int
    year: int
    name: str
    logo_url: str = None
    secretary: str = None
    secretary_contact: str = None
    course_name: str = None
    divisions: List[TournamentDivisionData] = []
    teams: List[TournamentTeamData] = []

class TournamentDataWithCount(SQLModel):
    num_tournaments: int
    tournaments: List[TournamentData]

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
    flight_query_data = session.exec(select(Flight, Course).join(Course).where(Flight.id.in_(flight_ids)).order_by(Flight.year))
    return [FlightData(
        flight_id=flight.id,
        year=flight.year,
        name=flight.name,
        logo_url=flight.logo_url,
        secretary=flight.secretary,
        secretary_contact=flight.secretary_contact,
        home_course_name=home_course.name
    ) for flight, home_course in flight_query_data]

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
    tournament_query_data = session.exec(select(Tournament, Course).join(Course).where(Tournament.id.in_(tournament_ids)).order_by(Tournament.year))
    return [TournamentData(
        tournament_id=tournament.id,
        year=tournament.year,
        name=tournament.name,
        logo_url=tournament.logo_url,
        secretary=tournament.secretary,
        secretary_contact=tournament.secretary_contact,
        course_name=course.name
    ) for tournament, course in tournament_query_data]

def get_divisions_in_flights(session: Session, flight_ids: List[int]) -> List[FlightDivisionData]:
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
    division_data : list of FlightDivisionData
        division data for division in the given flights
         
    """
    division_query_data = session.exec(select(Division, FlightDivisionLink, Tee).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(Tee, onclause=Tee.id == Division.primary_tee_id).where(FlightDivisionLink.flight_id.in_(flight_ids)))
    return [FlightDivisionData(
        division_id=division.id,
        flight_id=flight_division_link.flight_id,
        name=division.name,
        gender=division.gender,
        tee_name=home_tee.name,
        tee_rating=home_tee.rating,
        tee_slope=home_tee.slope
    ) for division, flight_division_link, home_tee in division_query_data]

def get_divisions_in_tournaments(session: Session, tournament_ids: List[int]) -> List[TournamentDivisionData]:
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
    division_data : list of TournamentDivisionData
        division data for division in the given tournaments

    """
    primary_tee = aliased(Tee)
    secondary_tee = aliased(Tee)
    division_query_data = session.exec(select(Division, TournamentDivisionLink, primary_tee, secondary_tee).join(TournamentDivisionLink, onclause=TournamentDivisionLink.division_id == Division.id).join(primary_tee, onclause=Division.primary_tee_id == primary_tee.id).join(secondary_tee, onclause=Division.secondary_tee_id == secondary_tee.id).where(TournamentDivisionLink.tournament_id.in_(tournament_ids)))
    return [TournamentDivisionData(
        division_id=division.id,
        tournament_id=tournament_division_link.tournament_id,
        name=division.name,
        gender=division.gender,
        primary_tee_name=primary_tee_db.name,
        primary_tee_rating=primary_tee_db.rating,
        primary_tee_slope=primary_tee_db.slope,
        secondary_tee_name=secondary_tee_db.name,
        secondary_tee_rating=secondary_tee_db.rating,
        secondary_tee_slope=secondary_tee_db.slope
    ) for division, tournament_division_link, primary_tee_db, secondary_tee_db in division_query_data]

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
    query_data = session.exec(select(Team, Flight).join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id).join(Flight, onclause=Flight.id == FlightTeamLink.flight_id).where(Flight.id.in_(flight_ids))).all()
    return [FlightTeamReadWithGolfers(id=team.id, flight_id=flight.id, name=team.name, golfers=team.golfers) for team, flight in query_data]

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
    query_data = session.exec(select(Team, Tournament).join(TournamentTeamLink, onclause=TournamentTeamLink.team_id == Team.id).join(Tournament, onclause=Tournament.id == TournamentTeamLink.tournament_id).where(Tournament.id.in_(tournament_ids))).all()
    return [TournamentTeamData(id=team.id, tournament_id=tournament.id, name=team.name, golfers=team.golfers) for team, tournament in query_data]

def get_golfers(session: Session, golfer_ids: List[int]) -> List[GolferData]:
    """
    Retrieves golfer data for the given golfers.
    
    Parameters
    ----------
    session : Session
        database session
    golfer_ids : list of integers
        golfer identifiers
        
    Returns
    -------
    golfer_data : list of GolferData
        golfer data for the given golfers

    """
    golfer_query_data = session.exec(select(Golfer).where(Golfer.id.in_(golfer_ids)))
    golfer_data = [GolferData(
        golfer_id=golfer.id,
        name=golfer.name,
        affiliation=golfer.affiliation
    ) for golfer in golfer_query_data]

    # Add team-golfer data to golfer data and return
    player_data = get_team_golfers(session=session, golfer_ids=golfer_ids)
    for g in golfer_data:
        g.team_golfer_data = [p for p in player_data if p.golfer_id == g.golfer_id]
    return golfer_data

def get_team_golfers(session: Session, golfer_ids: List[int]) -> List[TeamGolferData]:
    """
    Retrieves team golfer data for the given golfers.
    
    Parameters
    ----------
    session : Session
        database session
    golfer_ids : list of integers
        golfer identifiers

    Returns
    -------
    team_golfer_data : list of TeamGolferData
        team golfer data for the given golfers

    """
    query_data = session.exec(select(TeamGolferLink, Team, Golfer, Division, Flight).join(Team, onclause=TeamGolferLink.team_id == Team.id).join(Golfer, onclause=TeamGolferLink.golfer_id == Golfer.id).join(Division, onclause=TeamGolferLink.division_id == Division.id).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).join(Flight, onclause=FlightDivisionLink.flight_id == Flight.id).where(TeamGolferLink.golfer_id.in_(golfer_ids)))
    return [TeamGolferData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        flight_name=flight.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role
    ) for team_golfer_link, team, golfer, division, flight in query_data]

def get_team_golfers_for_teams(session: Session, team_ids: List[int]) -> List[TeamGolferData]:
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
    return [TeamGolferData(
        team_id=team_golfer_link.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        flight_name=flight.name,
        division_name=division.name,
        team_name=team.name,
        role=team_golfer_link.role
    ) for team_golfer_link, team, golfer, division, flight in query_data]

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
        golfer_handicap_index=round_golfer_link.golfer_handicap_index,
        golfer_playing_handicap=round_golfer_link.golfer_playing_handicap,
        team_name=team.name,
        course_name=course.name,
        track_name=track.name,
        tee_name=tee.name,
        tee_gender=tee.gender,
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
    round_ids = session.exec(select(Round.id).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id).join(TeamGolferLink, onclause=TeamGolferLink.golfer_id == Golfer.id).join(TournamentTeamLink, onclause=TournamentTeamLink.team_id == TeamGolferLink.team_id).where(TournamentTeamLink.tournament_id == tournament_id)).all()
    return get_tournament_rounds(session=session, round_ids=round_ids)

def get_tournament_rounds(session: Session, round_ids: List[int]) -> List[RoundData]:
    """
    Retrieves round data for the given tournament-play rounds, including results.

    TODO: Consolidate with `get_flight_rounds`.

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
    round_query_data = session.exec(select(Round, RoundGolferLink, Golfer, Course, Track, Tee).join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id).join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id).join(Tee).join(Track).join(Course).where(Round.id.in_(round_ids))).all()
    round_data = [RoundData(
        round_id=round.id,
        match_id=None, # TODO: remove match_id from RoundData
        team_id=None, # TODO: remove team_id from RoundData
        round_type=round.type,
        date_played=round.date_played,
        date_updated=round.date_updated,
        golfer_id=round_golfer_link.golfer_id,
        golfer_name=golfer.name,
        golfer_handicap_index=round_golfer_link.golfer_handicap_index,
        golfer_playing_handicap=round_golfer_link.golfer_playing_handicap,
        team_name=None, # TODO: remove team_name from RoundData
        course_name=course.name,
        track_name=track.name,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, round_golfer_link, golfer, course, track, tee in round_query_data]

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

def get_rounds_in_scoring_record(session: Session, golfer_id: int, date: date, limit: int = 20) -> List[RoundData]:
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
    date : date
        latest date allowed for rounds in this scoring record
    limit : int, optional
        maximum rounds allowed in scoring record
        Default: 20
    
    Returns
    -------
    record : list of RoundData
        round data for rounds in golfer's scoring record
    
    """
    round_ids = session.exec(select(Round.id).where(Round.golfer_id == golfer_id).where(Round.date_played <= date).order_by(desc(Round.date_played)).limit(limit)).all()
    return get_flight_rounds(session=session, round_ids=round_ids)
