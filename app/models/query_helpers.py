from typing import List
from sqlmodel import Session, select, SQLModel
from sqlalchemy.orm import aliased

from .course import Course
from .track import Track
from .tee import Tee
from .hole import Hole
from .flight import Flight, FlightData
from .team import Team, TeamData
from .player import Player, PlayerData
from .golfer import Golfer
from .division import Division, DivisionData
from .match import Match, MatchData
from .round import Round, RoundData
from .hole_result import HoleResult, HoleResultData
from .match_round_link import MatchRoundLink

from ..utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

# TODO: Move custom route data models elsewhere
class GolferData(SQLModel):
    golfer_id: int
    name: str
    affiliation: str
    player_data: List[PlayerData] = []

class GolferDataWithCount(SQLModel):
    num_golfers: int
    golfers: List[GolferData]
    
class TeamWithMatchData(SQLModel):
    team_id: int
    flight_id: int
    name: str
    players: List[PlayerData] = []
    matches: List[MatchData] = []

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
        home_course_name=home_course.name
    ) for flight, home_course in flight_query_data]

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
    division_query_data = session.exec(select(Division, Tee).join(Tee).where(Division.flight_id.in_(flight_ids)))
    return [DivisionData(
        division_id=division.id,
        flight_id=division.flight_id,
        name=division.name,
        gender=division.gender,
        home_tee_name=home_tee.name,
        home_tee_rating=home_tee.rating,
        home_tee_slope=home_tee.slope
    ) for division, home_tee in division_query_data]

def get_teams_in_flights(session: Session, flight_ids: List[int]) -> List[TeamData]:
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
    team_data : list of TeamData
        teams in the given flights
    
    """
    team_query_data = session.exec(select(Team).where(Team.flight_id.in_(flight_ids)))
    return [TeamData(
        team_id=team.id,
        flight_id=team.flight_id,
        name=team.name
    ) for team in team_query_data]

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

    # Add player data to golfer data and return
    player_data = get_players_for_golfers(session=session, golfer_ids=golfer_ids)
    for g in golfer_data:
        g.player_data = [p for p in player_data if p.golfer_id == g.golfer_id]
    return golfer_data

def get_players(session: Session, player_ids: List[int]) -> List[PlayerData]:
    """
    Retrieves player data for the given players.

    Parameters
    ----------
    session : Session
        database session
    player_ids : list of integers
        player identifiers

    Returns
    -------
    player_data : list of PlayerData
        player data for the given players
    
    """
    player_query_data = session.exec(select(Player, Team, Golfer, Division, Flight).join(Team, onclause=Player.team_id == Team.id).join(Golfer, onclause=Player.golfer_id == Golfer.id).join(Division, onclause=Player.division_id == Division.id).join(Flight, onclause=Division.flight_id == Flight.id).where(Player.id.in_(player_ids)))
    return [PlayerData(
        player_id=player.id,
        team_id=player.team_id,
        golfer_id=golfer.id,
        golfer_name=golfer.name,
        flight_name=flight.name,
        division_name=division.name,
        team_name=team.name,
        role=player.role
    ) for player, team, golfer, division, flight in player_query_data]

def get_players_for_golfers(session: Session, golfer_ids: List[int]) -> List[GolferData]:
    """
    Retrieves player data for the given golfers.

    Parameters
    ----------
    session : Session
        database session
    golfer_ids : list of integers
        golfer identifiers

    Returns
    -------
    player_data : list of PlayerData
        player data for the given golfers
    
    """
    player_ids = session.exec(select(Player.id).where(Player.golfer_id.in_(golfer_ids))).all()
    return get_players(session=session, player_ids=player_ids)

def get_players_in_teams(session: Session, team_ids: List[int]) -> List[PlayerData]:
    """
    Retrieves player data for all golfers in the given teams.

    Parameters
    ----------
    session : Session
        database session
    team_ids : list of integers
        team identifiers

    Returns
    -------
    player_data : list of PlayerData
        players in the given teams

    """
    player_ids = session.exec(select(Player.id).where(Player.team_id.in_(team_ids))).all()
    return get_players(session=session, player_ids=player_ids)

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
        match data for the given matches
    
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

def get_rounds(session: Session, round_ids: List[int]) -> List[RoundData]:
    """
    Retrieves round data for the given rounds, including results.

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
    round_query_data = session.exec(select(Round, MatchRoundLink, Golfer, Course, Tee, Team).join(MatchRoundLink, onclause=MatchRoundLink.round_id == Round.id).join(Match, onclause=Match.id == MatchRoundLink.match_id).join(Tee).join(Track).join(Course).join(Golfer).join(Player, ((Player.golfer_id == Round.golfer_id) & (Player.team_id.in_((Match.home_team_id, Match.away_team_id))))).join(Team, onclause=Player.team_id == Team.id).where(Round.id.in_(round_ids)))
    round_data = [RoundData(
        round_id=round.id,
        match_id=match_round_link.match_id,
        team_id=team.id,
        date_played=round.date_played,
        golfer_name=golfer.name,
        golfer_handicap_index=round.handicap_index,
        golfer_playing_handicap=round.playing_handicap,
        team_name=team.name,
        course_name=course.name,
        tee_name=tee.name,
        tee_gender=tee.gender,
        tee_rating=tee.rating,
        tee_slope=tee.slope,
        tee_color=tee.color if tee.color else "none",
    ) for round, match_round_link, golfer, course, tee, team in round_query_data]

    # Query hole data for selected rounds
    hole_result_data = get_hole_results_for_rounds(session=session, round_ids=[r.round_id for r in round_data])

    # Add hole data to round data and return
    # TODO: Compute handicap strokes and non-gross scores on entry to database
    ahs = APLLegacyHandicapSystem()
    for r in round_data:
        r.holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in r.holes])
        r.gross_score = sum([h.gross_score for h in r.holes])
        for h in r.holes:
            h.handicap_strokes = ahs.compute_hole_handicap_strokes(h.stroke_index, r.golfer_playing_handicap)
            h.adjusted_gross_score = ahs.compute_hole_adjusted_gross_score(h.par, h.stroke_index, h.gross_score, course_handicap=r.golfer_playing_handicap)
            h.net_score = h.gross_score - h.handicap_strokes
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in r.holes])
        r.net_score = sum([h.net_score for h in r.holes])
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
    return get_rounds(session=session, round_ids=round_ids)

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
    hole_query_data = session.exec(select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_(round_ids)))
    return [HoleResultData(
        hole_result_id=hole_result.id,
        round_id=hole_result.round_id,
        hole_id=hole_result.hole_id,
        number=hole.number,
        par=hole.par,
        yardage=hole.yardage,
        stroke_index=hole.stroke_index,
        gross_score=hole_result.strokes
    ) for hole_result, hole in hole_query_data]
