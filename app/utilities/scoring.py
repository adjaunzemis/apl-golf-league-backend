from ..models.hole_result import HoleResultValidationResponse
from ..models.round import RoundValidationRequest, RoundValidationResponse
from .apl_handicap_system import APLHandicapSystem
from .apl_legacy_handicap_system import APLLegacyHandicapSystem


def validate_round(round: RoundValidationRequest):
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
