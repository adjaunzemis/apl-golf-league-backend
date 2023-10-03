from datetime import datetime, date
from typing import Union

from ..models.hole_result import HoleResultValidationResponse
from ..models.round import RoundValidationRequest, RoundValidationResponse
from ..models.match import (
    MatchHoleWinner,
    MatchValidationRequest,
    MatchValidationResponse,
    MatchHoleResult,
)
from .apl_handicap_system import APLHandicapSystem
from .apl_legacy_handicap_system import APLLegacyHandicapSystem


def validate_round(round: RoundValidationRequest) -> RoundValidationResponse:
    """Determines whether a given round is valid under the relevant handicap system.

    Checks whether the gross score is strictly positive and less than the max allowed.
    Aggregates per-hole validity into round validity.

    Parameters
    ----------
    round: RoundValidationRequest
        round data to be validated

    Returns
    -------
    response: RoundValidationResponse
        round data with validation

    """
    # Determine handicapping system by year
    # TODO: Make a utility/factory for this
    if round.date_played.year >= 2022:
        ahs = APLHandicapSystem()
    else:
        ahs = APLLegacyHandicapSystem()

    # Prepare round response
    round_response = RoundValidationResponse(
        date_played=round.date_played, course_handicap=round.course_handicap
    )

    for hole in round.holes:
        # Compute handicapping scores for this hole
        handicap_strokes = ahs.compute_hole_handicap_strokes(
            hole.stroke_index, round.course_handicap
        )
        adjusted_gross_score = ahs.compute_hole_adjusted_gross_score(
            hole.par, hole.stroke_index, hole.gross_score, round.course_handicap
        )
        net_score = hole.gross_score - handicap_strokes
        max_gross_score = ahs.compute_hole_maximum_strokes(hole.par, handicap_strokes)

        # Populate hole validation response
        hole_response = HoleResultValidationResponse(
            number=hole.number,
            par=hole.par,
            stroke_index=hole.stroke_index,
            gross_score=hole.gross_score,
            handicap_strokes=handicap_strokes,
            adjusted_gross_score=adjusted_gross_score,
            net_score=net_score,
            max_gross_score=max_gross_score,
        )

        # Update validity for this hole
        hole_response.is_valid = (
            hole_response.gross_score > 0
            and hole_response.gross_score <= hole_response.max_gross_score
        )

        # Add hole to round response
        round_response.holes.append(hole_response)

    # Update validity for this round and return
    round_response.is_valid = all([hole.is_valid for hole in round_response.holes])
    return round_response


def validate_match(match: MatchValidationRequest) -> MatchValidationResponse:
    """Determines whether a given match is valid under the relevant handicap system.

    Validates each round.
    Determines per-hole winning team and each team's match score.
    Aggregates per-round validity into match validity.

    Parameters
    ----------
    match: MatchValidationRequest
        match data to be validated

    Returns
    -------
    response: MatchValidationResponse
        match data with validation

    """
    # Determine handicapping system by year
    # TODO: Make a utility/factory for this
    date_played = match.home_team_rounds[0].date_played
    if date_played.year >= 2022:
        ahs = APLHandicapSystem()
    else:
        ahs = APLLegacyHandicapSystem()

    # Validate rounds
    home_team_round_responses: list[RoundValidationResponse] = []
    for home_team_round in match.home_team_rounds:
        home_team_round_responses.append(validate_round(home_team_round))

    away_team_round_responses: list[RoundValidationResponse] = []
    for away_team_round in match.away_team_rounds:
        away_team_round_responses.append(validate_round(away_team_round))

    # Initialize match response, check for match validity
    match_response = MatchValidationResponse(
        home_team_rounds=home_team_round_responses,
        away_team_rounds=away_team_round_responses,
    )
    match_response.is_valid = all(
        [response.is_valid for response in home_team_round_responses]
    ) and all([response.is_valid for response in away_team_round_responses])

    if match_response.is_valid:
        # Compute match hole-by-hole results and team net scores
        match_hole_results: list[MatchHoleResult] = []

        home_team_course_handicaps = [
            r.course_handicap for r in match_response.home_team_rounds
        ]
        away_team_course_handicaps = [
            r.course_handicap for r in match_response.away_team_rounds
        ]

        for hole_idx in range(len(match_response.home_team_rounds[0].holes)):
            home_team_gross_scores = [
                r.holes[hole_idx].gross_score for r in match_response.home_team_rounds
            ]
            away_team_gross_scores = [
                r.holes[hole_idx].gross_score for r in match_response.away_team_rounds
            ]

            (
                home_team_handicap_strokes,
                away_team_handicap_strokes,
            ) = ahs.compute_match_team_hole_handicap_strokes(
                stroke_index=match_response.home_team_rounds[0]
                .holes[hole_idx]
                .stroke_index,
                team_course_handicaps=home_team_course_handicaps,
                opponent_course_handicaps=away_team_course_handicaps,
            )

            match_hole_results.append(
                ahs.compute_match_hole_result(
                    home_team_gross_scores=home_team_gross_scores,
                    home_team_handicap_strokes=home_team_handicap_strokes,
                    away_team_gross_scores=away_team_gross_scores,
                    away_team_handicap_strokes=away_team_handicap_strokes,
                )
            )

        # Compute match score
        (home_score, away_score) = compute_match_score(
            hole_winners=[r.winner for r in match_hole_results],
            home_net_scores=[
                sum([h.net_score for h in r.holes])
                for r in match_response.home_team_rounds
            ],
            away_net_scores=[
                sum([h.net_score for h in r.holes])
                for r in match_response.away_team_rounds
            ],
            date_played=date_played,
        )
        match_response.home_team_score = home_score
        match_response.away_team_score = away_score
        match_response.hole_results = match_hole_results

    # Return populated match response
    return match_response


def compute_match_score(
    hole_winners: list[MatchHoleWinner],
    home_net_scores: list[int],
    away_net_scores: list[int],
    date_played: Union[datetime, date],
):
    """Computes match score based on hole-by-hole winners and player net scores.

    Parameters
    ----------
    hole_winners: list[MatchHoleWinner]
        winning team for each hole of the match
    home_net_scores: list[int]
        total net score for each round for the home team
    away_net_scores: list[int]
        total net score for each round for the away team
    date_played: datetime | date
        date that the match was played

    Returns
    -------
    home_score: float
        points earned by home team
    away_score: float
        points earned by away team

    """
    # Determine handicapping system by year
    # TODO: Make a utility/factory for this
    if date_played.year >= 2022:
        ahs = APLHandicapSystem()
    else:
        ahs = APLLegacyHandicapSystem()

    # Initialize team scores
    home_score = 0.0
    away_score = 0.0

    # Add points based on hole-by-hole results
    for winner in hole_winners:
        if winner == MatchHoleWinner.HOME:
            home_score += ahs.match_points_for_winning_hole
            away_score += ahs.match_points_for_losing_hole
        elif winner == MatchHoleWinner.AWAY:
            home_score += ahs.match_points_for_losing_hole
            away_score += ahs.match_points_for_winning_hole
        else:
            home_score += ahs.match_points_for_tying_hole
            away_score += ahs.match_points_for_tying_hole

    # Add points based on team net results
    home_team_net_score = sum(home_net_scores)
    away_team_net_score = sum(away_net_scores)
    if home_team_net_score < away_team_net_score:
        home_score += ahs.match_points_for_winning_total_net_score
        away_score += ahs.match_points_for_losing_total_net_score
    elif away_team_net_score < home_team_net_score:
        home_score += ahs.match_points_for_losing_total_net_score
        away_score += ahs.match_points_for_winning_total_net_score
    else:
        home_score += ahs.match_points_for_tying_total_net_score
        away_score += ahs.match_points_for_tying_total_net_score

    return (home_score, away_score)
