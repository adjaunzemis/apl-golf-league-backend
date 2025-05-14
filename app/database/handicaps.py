from sqlmodel import Session, select

from app.models.course import Course
from app.models.golfer import Golfer
from app.models.handicap import HandicapIndex, ScoringRecordRound
from app.models.hole_result import HoleResult
from app.models.qualifying_score import QualifyingScore
from app.models.round import Round, RoundType, ScoringType
from app.models.round_golfer_link import RoundGolferLink
from app.models.tee import Tee
from app.models.track import Track
from app.utilities.apl_handicap_system import APLHandicapSystem


def get_handicap_history_for_golfer(
    session: Session, golfer_id: int
) -> list[HandicapIndex]:
    """Get handicap index history for a specific golfer.

    Parameters
    ----------
    session (`Session`): Database session.

    """
    return list(
        session.exec(
            select(HandicapIndex)
            .where(HandicapIndex.golfer_id == golfer_id)
            .order_by(HandicapIndex.date_posted, HandicapIndex.round_number)
        )
    )


def get_scoring_record_rounds_for_golfer(
    session: Session, golfer_id: int, year: int | None = None
) -> list[ScoringRecordRound]:
    """Gathers list of scoring record rounds for"""
    ahs = APLHandicapSystem()  # TODO: Inject? Determine by time range?

    scoring_record: list[ScoringRecordRound] = []

    golfer_db = session.get(Golfer, golfer_id)
    if golfer_db is None:
        return scoring_record

    # Qualifying scores
    quals_db = session.exec(
        select(QualifyingScore)
        .where(QualifyingScore.golfer_id == golfer_id)
        .order_by(QualifyingScore.date_played, QualifyingScore.id)
    ).all()

    for qual_db in quals_db:
        scoring_record.append(
            ScoringRecordRound(
                golfer_id=golfer_id,
                golfer_name=golfer_db.name,
                round_id=None,
                date_played=qual_db.date_played,
                round_type=RoundType.QUALIFYING,
                scoring_type=ScoringType.INDIVIDUAL,
                course_name=qual_db.course_name,
                track_name=qual_db.track_name,
                tee_name=qual_db.tee_name,
                tee_par=qual_db.tee_par,
                tee_rating=qual_db.tee_rating,
                tee_slope=qual_db.tee_slope,
                playing_handicap=None,
                gross_score=qual_db.gross_score,
                adjusted_gross_score=qual_db.adjusted_gross_score,
                net_score=None,
                score_differential=qual_db.score_differential,
                handicap_index=None,
            )
        )

    # Set handicap index on last qualifying score
    scoring_record[-1].handicap_index = ahs.compute_handicap_index(
        record=[sr.score_differential for sr in scoring_record]
    )

    # League rounds
    round_data_db: list[tuple[Round, RoundGolferLink, Tee, Track, Course]] = (
        session.exec(
            select(Round, RoundGolferLink, Tee, Track, Course)
            .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
            .join(Tee, onclause=Tee.id == Round.tee_id)
            .join(Track, onclause=Track.id == Tee.track_id)
            .join(Course, onclause=Course.id == Track.course_id)
            .where(RoundGolferLink.golfer_id == golfer_id)
            .where(Round.scoring_type == ScoringType.INDIVIDUAL)
            .order_by(Round.date_played, Round.id)
        ).all()
    )

    for round_db, rgl_db, tee_db, track_db, course_db in round_data_db:
        hole_results_db = session.exec(
            select(HoleResult).where(HoleResult.round_id == round_db.id)
        ).all()

        gross_score = sum(hr_db.gross_score for hr_db in hole_results_db)
        adjusted_gross_score = sum(
            hr_db.adjusted_gross_score for hr_db in hole_results_db
        )
        net_score = sum(hr_db.net_score for hr_db in hole_results_db)

        score_differential = ahs.compute_score_differential(
            rating=tee_db.rating, slope=tee_db.slope, score=adjusted_gross_score
        )

        hcp_scoring_record = list(
            filter(lambda srr: srr.round_type != RoundType.QUALIFYING, scoring_record)
        )
        if len(hcp_scoring_record) < 1:  # include qualifying scores
            hcp_scoring_record = scoring_record

        # Note: only include up to prior 9 scores
        hcp_score_differentials = [
            srr.score_differential for srr in hcp_scoring_record[-9:]
        ]
        hcp_score_differentials.append(score_differential)

        scoring_record.append(
            ScoringRecordRound(
                golfer_id=golfer_id,
                golfer_name=golfer_db.name,
                round_id=round_db.id,
                date_played=round_db.date_played,
                round_type=round_db.type,
                scoring_type=round_db.scoring_type,
                course_name=course_db.name,
                track_name=track_db.name,
                tee_name=tee_db.name,
                tee_par=tee_db.par,
                tee_rating=tee_db.rating,
                tee_slope=tee_db.slope,
                playing_handicap=rgl_db.playing_handicap,
                gross_score=gross_score,
                adjusted_gross_score=adjusted_gross_score,
                net_score=net_score,
                score_differential=score_differential,
                handicap_index=ahs.compute_handicap_index(
                    record=hcp_score_differentials
                ),
            )
        )

    # Filter by year
    if year is None:
        return scoring_record

    scoring_record_limit = list(
        filter(lambda srr: srr.date_played.year <= year, scoring_record)
    )
    scoring_record_year = list(
        filter(lambda srr: srr.date_played.year == year, scoring_record)
    )

    if len(scoring_record_year) < 10:
        return scoring_record_limit[-10:]

    return scoring_record_year
