from datetime import date as dt_date
from datetime import datetime, timedelta
from typing import List, Optional

from sqlmodel import Session, SQLModel, desc, select

from app.models.course import Course
from app.models.golfer import Golfer
from app.models.hole import Hole
from app.models.hole_result import HoleResult, HoleResultData
from app.models.qualifying_score import QualifyingScore
from app.models.round import Round, RoundSummary, RoundType, ScoringType
from app.models.round_golfer_link import RoundGolferLink
from app.models.tee import Tee
from app.models.track import Track
from app.utilities.apl_handicap_system import APLHandicapSystem
from app.utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem


class HandicapIndexData(SQLModel):
    active_date: str
    active_handicap_index: float = None
    active_rounds: Optional[List[RoundSummary]] = None
    pending_handicap_index: Optional[float] = None
    pending_rounds: Optional[List[RoundSummary]] = None


def get_hole_results_for_rounds(
    session: Session, round_ids: List[int]
) -> List[HoleResultData]:
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
    hole_query_data = session.exec(
        select(HoleResult, Hole).join(Hole).where(HoleResult.round_id.in_(round_ids))
    )
    return [
        HoleResultData(
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
            net_score=hole_result.net_score,
        )
        for hole_result, hole in hole_query_data
    ]


def get_round_summaries(
    session: Session, round_ids: List[int], use_legacy_handicapping: bool = False
) -> List[RoundSummary]:
    """ """
    if use_legacy_handicapping:
        handicap_system = APLLegacyHandicapSystem()
    else:
        handicap_system = APLHandicapSystem()

    round_query_data = session.exec(
        select(Round, RoundGolferLink, Golfer, Course, Track, Tee)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
        .join(Tee)
        .join(Track)
        .join(Course)
        .where(Round.id.in_(round_ids))
    ).all()
    round_summaries = [
        RoundSummary(
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
        )
        for round, round_golfer_link, golfer, course, track, tee in round_query_data
    ]

    # Query hole data for selected rounds
    hole_result_data = get_hole_results_for_rounds(session=session, round_ids=round_ids)

    # Add hole data to round data and return
    for r in round_summaries:
        round_holes = [h for h in hole_result_data if h.round_id == r.round_id]
        r.tee_par = sum([h.par for h in round_holes])
        r.gross_score = sum([h.gross_score for h in round_holes])
        r.adjusted_gross_score = sum([h.adjusted_gross_score for h in round_holes])
        r.net_score = sum([h.net_score for h in round_holes])
        r.score_differential = handicap_system.compute_score_differential(
            r.tee_rating, r.tee_slope, r.adjusted_gross_score
        )
    return round_summaries


def get_rounds_in_scoring_record(
    session: Session,
    golfer_id: int,
    min_date: dt_date,
    max_date: dt_date,
    limit: int = 20,
    use_legacy_handicapping: bool = False,
) -> List[RoundSummary]:
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
    rounds : list of RoundResults
        round results for rounds in golfer's scoring record

    """
    round_ids = session.exec(
        select(Round.id)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .where(RoundGolferLink.golfer_id == golfer_id)
        .where(Round.scoring_type == ScoringType.INDIVIDUAL)
        .where(Round.date_played >= min_date)
        .where(Round.date_played <= max_date)
        .order_by(desc(Round.date_played))
        .limit(limit)
    ).all()
    round_summaries = get_round_summaries(
        session=session,
        round_ids=round_ids,
        use_legacy_handicapping=use_legacy_handicapping,
    )
    if len(round_summaries) < 2:  # include qualifying scores
        qualifying_scores_db = session.exec(
            select(QualifyingScore)
            .where(QualifyingScore.golfer_id == golfer_id)
            .where(QualifyingScore.year >= min_date.year)
        ).all()
        for qualifying_score_db in qualifying_scores_db:
            round_summaries.append(
                RoundSummary(
                    round_type=RoundType.QUALIFYING,
                    date_played=qualifying_score_db.date_played,
                    date_updated=qualifying_score_db.date_updated,
                    course_name=f"Qualifying Score: {qualifying_score_db.course_name if qualifying_score_db.course_name is not None else qualifying_score_db.type}",
                    track_name=(
                        qualifying_score_db.track_name
                        if qualifying_score_db.track_name is not None
                        else None
                    ),
                    tee_name=(
                        qualifying_score_db.tee_name
                        if qualifying_score_db.tee_name is not None
                        else None
                    ),
                    tee_gender=(
                        qualifying_score_db.tee_gender
                        if qualifying_score_db.tee_gender is not None
                        else None
                    ),
                    tee_par=(
                        qualifying_score_db.tee_par
                        if qualifying_score_db.tee_par is not None
                        else None
                    ),
                    tee_rating=(
                        qualifying_score_db.tee_rating
                        if qualifying_score_db.tee_rating is not None
                        else None
                    ),
                    tee_slope=(
                        qualifying_score_db.tee_slope
                        if qualifying_score_db.tee_slope is not None
                        else None
                    ),
                    gross_score=(
                        qualifying_score_db.gross_score
                        if qualifying_score_db.gross_score is not None
                        else None
                    ),
                    adjusted_gross_score=(
                        qualifying_score_db.adjusted_gross_score
                        if qualifying_score_db.adjusted_gross_score is not None
                        else None
                    ),
                    score_differential=qualifying_score_db.score_differential,
                )
            )
    return sorted(
        round_summaries,
        key=lambda round_summary: round_summary.date_played,
        reverse=True,
    )


def get_handicap_index_data(
    session: Session,
    golfer_id: int,
    min_date: dt_date,
    max_date: dt_date,
    limit: int = 20,
    include_rounds: bool = False,
    use_legacy_handicapping: bool = False,
) -> HandicapIndexData:
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
    active_rounds = get_rounds_in_scoring_record(
        session=session,
        golfer_id=golfer_id,
        min_date=min_date,
        max_date=max_date,
        limit=limit,
        use_legacy_handicapping=use_legacy_handicapping,
    )
    active_record = [r.score_differential for r in active_rounds]
    if len(active_record) > 0:
        active_index = handicap_system.compute_handicap_index(record=active_record)
    # Process pending scoring record (between max_date and now)
    pending_rounds = []
    pending_index = None
    pending_date_start = max_date + timedelta(days=1)
    if datetime.today().date() > pending_date_start:
        pending_rounds = get_rounds_in_scoring_record(
            session=session,
            golfer_id=golfer_id,
            min_date=pending_date_start,
            max_date=datetime.today() + timedelta(days=1),
            limit=limit,
            use_legacy_handicapping=use_legacy_handicapping,
        )
        pending_record = [r.score_differential for r in pending_rounds]
        if len(pending_record) < limit:
            pending_record = pending_record + active_record[: -len(pending_rounds)]
        if len(pending_record) > 0:
            pending_index = handicap_system.compute_handicap_index(
                record=pending_record
            )
    # Return results
    data = HandicapIndexData(
        active_date=datetime.combine(max_date, datetime.min.time())
        .astimezone()
        .replace(microsecond=0)
        .isoformat(),
        active_handicap_index=active_index,
        pending_handicap_index=pending_index,
        active_rounds=None,
        pending_rounds=None,
    )
    if include_rounds:
        data.active_rounds = active_rounds
        data.pending_rounds = pending_rounds
    return data


def update_golfer_handicaps(
    *,
    session: Session,
    prior_end_date: dt_date,
    new_end_date: dt_date,
    min_date: dt_date | None = None,
    golfer_id: int | None = None,
    force_update: bool = False,
    dry_run: bool = False,
):
    """
    Updates handicap index for each golfer with pending rounds.

    Parameters
    ----------
    session : Session
        database session
    prior_end_date : datetime
        end date of prior handicap update
    new_end_date : datetime
        end date for current handicap update
    min_date: datetime | None
        earliest allowed date for rounds in scoring record
        Default: None, uses default (last three calendar years)
    golfer_id: int | None
        specific golfer to update handicap index
        Default: None, all golfers
    force_update: bool, optional
        if true, updates handicap index regardless of mismatches or pending rounds
        Default: False
    dry_run : bool, optional
        if true, does not commit changes to database records
        Default: False

    """
    print(
        f"Starting handicap update: prior={prior_end_date}, new={new_end_date}, force_update={force_update}"
    )
    if dry_run:
        print(f"NOTE: Dry-run, won't commit changes to database!")

    if min_date is None:
        min_date = datetime(datetime.today().year - 3, 1, 1).date()
    print(f"Minimum date for rounds in handicap consideration: {min_date}")

    if golfer_id is not None:
        golfer_db = session.exec(
            select(Golfer).where(Golfer.id == golfer_id)
        ).one_or_none()
        if golfer_db is None:
            raise ValueError(
                f"Unable to find golfer with id= {golfer_id} for handicap update"
            )
        golfers_db = [golfer_db]
    else:
        golfers_db = session.exec(select(Golfer).order_by(Golfer.id)).all()

    updates_info: list[dict] = []
    for golfer_db in golfers_db:
        prior_handicap_index_data = get_handicap_index_data(
            session=session,
            golfer_id=golfer_db.id,
            min_date=min_date,
            max_date=prior_end_date,
            limit=10,
            include_rounds=True,
            use_legacy_handicapping=False,
        )
        new_handicap_index_data = get_handicap_index_data(
            session=session,
            golfer_id=golfer_db.id,
            min_date=min_date,
            max_date=new_end_date,
            limit=10,
            include_rounds=True,
            use_legacy_handicapping=False,
        )

        current_handicap_index = golfer_db.handicap_index
        new_handicap_index = new_handicap_index_data.active_handicap_index

        if current_handicap_index is None and new_handicap_index is None:
            continue

        update_required = False
        update_reasons = []
        if force_update:
            update_required = True
            update_reasons.append("forced")

        if new_handicap_index != current_handicap_index:
            update_required = True
            update_reasons.append("golfer handicap index mismatch")

        for pending_round in prior_handicap_index_data.pending_rounds:
            if pending_round in new_handicap_index_data.active_rounds:
                update_required = True
                update_reasons.append("pending rounds")
                break

        if update_required:
            print(
                f"Updating handicap index for '{golfer_db.name}' (id={golfer_db.id}): db={current_handicap_index}, prior={prior_handicap_index_data.active_handicap_index}, new={new_handicap_index} : "
                + ", ".join(update_reasons)
            )
            updates_info.append(
                {
                    "golfer_name": golfer_db.name,
                    "golfer_id": golfer_db.id,
                    "index_prior": current_handicap_index,
                    "index_new": new_handicap_index,
                    "reasons": ", ".join(update_reasons),
                }
            )
            golfer_db.handicap_index = new_handicap_index
            golfer_db.handicap_index_updated = datetime.now()
            if not dry_run:
                session.add(golfer_db)

    if not dry_run:
        session.commit()  # update all handicaps at once

    print(f"Completed handicap update!")
    return updates_info


def recalculate_hole_results(
    *, session: Session, year: int = 2022, dry_run: bool = False
):
    """
    Recalculates hole results for any rounds played in the given year.

    If a discrepancy is found between the (new) calculated values and the
    (old) database values, the database is updated.

    Based on error from early 2022 season in adjusted gross calculation.

    Parameters
    ----------
    session : Session
        database session
    year : int, optional
        year for rounds played to be analyzed and corrected
        Default: 2022
    dry_run : bool, optional
        if true, does not commit changes to database records
        Default: False

    """
    print(f"Recalculating hole results for {year} season")
    ahs = APLHandicapSystem()
    round_data = session.exec(
        select(Round, RoundGolferLink, Golfer)
        .join(RoundGolferLink, onclause=RoundGolferLink.round_id == Round.id)
        .join(Golfer, onclause=Golfer.id == RoundGolferLink.golfer_id)
        .where(Round.date_played >= datetime(year, 1, 1))
    ).all()
    print(f"Analyzing {len(round_data)} rounds")
    round_error_counter = 0
    for round_db, round_golfer_link_db, golfer_db in round_data:
        hole_results_db = session.exec(
            select(HoleResult).where(HoleResult.round_id == round_db.id)
        ).all()
        error_found_in_round = False
        for hole_result_db in hole_results_db:
            hole_db = hole_result_db.hole
            handicap_strokes = ahs.compute_hole_handicap_strokes(
                stroke_index=hole_db.stroke_index,
                course_handicap=round_golfer_link_db.playing_handicap,
            )
            adj_gross_score = ahs.compute_hole_adjusted_gross_score(
                par=hole_db.par,
                stroke_index=hole_db.stroke_index,
                score=hole_result_db.gross_score,
                course_handicap=round_golfer_link_db.playing_handicap,
            )
            net_score = hole_result_db.gross_score - handicap_strokes
            if (
                (handicap_strokes != hole_result_db.handicap_strokes)
                or (adj_gross_score != hole_result_db.adjusted_gross_score)
                or (net_score != hole_result_db.net_score)
            ):
                if not error_found_in_round:
                    print(
                        f"Golfer: {golfer_db.name}, Date: {round_db.date_played}, Course Handicap: {round_golfer_link_db.playing_handicap}"
                    )
                    error_found_in_round = True
                    round_error_counter += 1
                print(
                    f"Hole #{hole_db.number}: Par={hole_db.par}, SI={hole_db.stroke_index}, HS={handicap_strokes}, Gross={hole_result_db.gross_score}, Old AG={hole_result_db.adjusted_gross_score}, New AG={adj_gross_score}"
                )
                hole_result_db.handicap_strokes = handicap_strokes
                hole_result_db.adjusted_gross_score = adj_gross_score
                hole_result_db.net_score = net_score
                if not dry_run:
                    session.add(hole_result_db)
                    session.commit()
                    session.refresh(hole_result_db)
            if error_found_in_round:
                round_db.date_updated = datetime.now()
                if not dry_run:
                    session.add(round_db)
                    session.commit()
                    session.refresh(round_db)
    print(f"Corrected errors in {round_error_counter} rounds")
