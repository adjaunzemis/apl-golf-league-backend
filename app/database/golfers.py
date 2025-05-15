from sqlmodel import Session, select

from app.models.golfer import Golfer, GolferStatistics
from app.models.hole import Hole
from app.models.hole_result import HoleResult
from app.models.round import Round, ScoringType
from app.models.round_golfer_link import RoundGolferLink


def get_statistics(
    session: Session, golfer_id: int, year: int | None = None
) -> GolferStatistics | None:
    golfer_db = session.get(Golfer, golfer_id)
    if golfer_db is None:
        return None

    rounds_db = session.exec(
        select(Round)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .where(RoundGolferLink.golfer_id == golfer_id)
        .where(Round.scoring_type == ScoringType.INDIVIDUAL)
    ).all()
    if year is not None:
        rounds_db = [
            round_db for round_db in rounds_db if round_db.date_played.year == year
        ]

    golfer_stats = GolferStatistics(
        golfer_id=golfer_db.id,
        golfer_name=golfer_db.name,
    )
    for round_db in rounds_db:
        golfer_stats.num_rounds += 1  # TODO: track repeat rounds

        par = 0
        gross_score = 0
        net_score = 0

        round_data = session.exec(
            select(HoleResult, Hole)
            .join(Hole, onclause=Hole.id == HoleResult.hole_id)
            .where(HoleResult.round_id == round_db.id)
        ).all()
        for hole_result, hole in round_data:
            golfer_stats.num_holes += 1

            par += hole.par

            # Gross scoring (hole)
            gross_score += hole_result.gross_score

            if hole_result.gross_score <= 1:
                golfer_stats.gross_scoring.num_aces += 1
            elif hole_result.gross_score == (hole.par - 3):
                golfer_stats.gross_scoring.num_albatrosses += 1
            elif hole_result.gross_score == (hole.par - 2):
                golfer_stats.gross_scoring.num_eagles += 1
            elif hole_result.gross_score == (hole.par - 1):
                golfer_stats.gross_scoring.num_birdies += 1
            elif hole_result.gross_score == hole.par:
                golfer_stats.gross_scoring.num_pars += 1
            elif hole_result.gross_score == (hole.par + 1):
                golfer_stats.gross_scoring.num_bogeys += 1
            elif hole_result.gross_score == (hole.par + 2):
                golfer_stats.gross_scoring.num_double_bogeys += 1
            elif hole_result.gross_score > (hole.par + 2):
                golfer_stats.gross_scoring.num_others += 1

            # Gross scoring (hole)
            net_score += hole_result.net_score

            if hole_result.net_score <= 1:
                golfer_stats.net_scoring.num_aces += 1
            elif hole_result.net_score == (hole.par - 3):
                golfer_stats.net_scoring.num_albatrosses += 1
            elif hole_result.net_score == (hole.par - 2):
                golfer_stats.net_scoring.num_eagles += 1
            elif hole_result.net_score == (hole.par - 1):
                golfer_stats.net_scoring.num_birdies += 1
            elif hole_result.net_score == hole.par:
                golfer_stats.net_scoring.num_pars += 1
            elif hole_result.net_score == (hole.par + 1):
                golfer_stats.net_scoring.num_bogeys += 1
            elif hole_result.net_score == (hole.par + 2):
                golfer_stats.net_scoring.num_double_bogeys += 1
            elif hole_result.net_score > (hole.par + 2):
                golfer_stats.net_scoring.num_others += 1

            # Scoring by hole type
            if hole.par == 3:
                golfer_stats.num_par_3_holes += 1
                golfer_stats.gross_scoring.avg_par_3_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_3_score
                ) / golfer_stats.num_par_3_holes
                golfer_stats.net_scoring.avg_par_3_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_3_score
                ) / golfer_stats.num_par_3_holes
            elif hole.par == 4:
                golfer_stats.num_par_4_holes += 1
                golfer_stats.gross_scoring.avg_par_4_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_4_score
                ) / golfer_stats.num_par_4_holes
                golfer_stats.net_scoring.avg_par_4_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_4_score
                ) / golfer_stats.num_par_4_holes
            elif hole.par == 5:
                golfer_stats.num_par_5_holes += 1
                golfer_stats.gross_scoring.avg_par_5_score += (
                    hole_result.gross_score - golfer_stats.gross_scoring.avg_par_5_score
                ) / golfer_stats.num_par_5_holes
                golfer_stats.net_scoring.avg_par_5_score += (
                    hole_result.net_score - golfer_stats.net_scoring.avg_par_5_score
                ) / golfer_stats.num_par_5_holes

        # Gross scoring (round)
        golfer_stats.gross_scoring.avg_score += (
            gross_score - golfer_stats.gross_scoring.avg_score
        ) / golfer_stats.num_rounds
        golfer_stats.gross_scoring.avg_score_to_par += (
            (gross_score - par) - golfer_stats.gross_scoring.avg_score_to_par
        ) / golfer_stats.num_rounds

        # Net scoring (round)
        golfer_stats.net_scoring.avg_score += (
            net_score - golfer_stats.net_scoring.avg_score
        ) / golfer_stats.num_rounds
        golfer_stats.net_scoring.avg_score_to_par += (
            (net_score - par) - golfer_stats.net_scoring.avg_score_to_par
        ) / golfer_stats.num_rounds

    return golfer_stats
