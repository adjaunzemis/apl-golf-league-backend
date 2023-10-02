from datetime import datetime, date
from typing import Union

from ..models.hole_result import HoleResultValidationResponse
from ..models.round import RoundValidationRequest, RoundValidationResponse
from ..models.match import (
    MatchValidationRequest,
    MatchValidationResponse,
    MatchTeamDesignator,
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

    # TODO: Calculate hole-by-hole team handicaps
    team_receiving_handicap_strokes = MatchTeamDesignator.HOME  # TODO: Implement
    team_handicap = 0  # TODO: Implement
    team_handicap_strokes_received = [
        ahs.compute_hole_handicap_strokes(
            stroke_index=hole.stroke_index, course_handicap=team_handicap
        )
        for hole in match.home_team_rounds[0].holes
    ]

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
        home_team_net_score = 0.0
        away_team_net_score = 0.0
        for hole_idx in range(len(match_response.home_team_rounds[0].holes)):
            home_team_gross_scores = [
                round.holes[hole_idx].gross_score
                for round in match_response.home_team_rounds
            ]
            away_team_gross_scores = [
                round.holes[hole_idx].gross_score
                for round in match_response.away_team_rounds
            ]
            match_hole_results.append(
                ahs.determine_match_hole_result(
                    home_team_gross_scores,
                    away_team_gross_scores,
                    team_receiving_handicap_strokes,
                    team_handicap_strokes_received[hole_idx],
                )
            )

            home_team_net_score += sum(
                [
                    round.holes[hole_idx].net_score
                    for round in match_response.home_team_rounds
                ]
            )
            away_team_net_score += sum(
                [
                    round.holes[hole_idx].net_score
                    for round in match_response.away_team_rounds
                ]
            )

        # Compute match score
        (home_score, away_score) = compute_match_score(
            match_hole_results, home_team_net_score, away_team_net_score, date_played
        )
        match_response.home_team_score = home_score
        match_response.away_team_score = away_score
        match_response.hole_results = match_hole_results

    # Return populated match response
    return match_response


def compute_match_score(
    match_hole_results: list[MatchHoleResult],
    home_net_score: int,
    away_net_score: int,
    date_played: Union[datetime, date],
):
    """Computes match score based on hole-by-hole winners and team net scores.

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
    for match_hole_result in match_hole_results:
        if match_hole_result == MatchTeamDesignator.HOME:
            home_score += ahs.match_points_for_winning_hole
            away_score += ahs.match_points_for_losing_hole
        elif match_hole_result == MatchTeamDesignator.AWAY:
            home_score += ahs.match_points_for_losing_hole
            away_score += ahs.match_points_for_winning_hole
        else:
            home_score += ahs.match_points_for_tying_hole
            away_score += ahs.match_points_for_tying_hole

    # Add points based on team net results
    if home_net_score < away_net_score:
        home_score += ahs.match_points_for_winning_total_net_score
        away_score += ahs.match_points_for_losing_total_net_score
    elif away_net_score < home_net_score:
        home_score += ahs.match_points_for_losing_total_net_score
        away_score += ahs.match_points_for_winning_total_net_score
    else:
        home_score += ahs.match_points_for_tying_total_net_score
        away_score += ahs.match_points_for_tying_total_net_score

    return (home_score, away_score)
