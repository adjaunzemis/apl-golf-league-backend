from datetime import datetime

import pytest
from sqlmodel import Session

from app.database import rounds as db_round
from app.models.round import Round, RoundType, ScoringType


@pytest.mark.parametrize(
    "num_rounds, query_ids", [(1, [1]), (3, [2, 3]), (5, [10]), (5, [2, 10])]
)
def test_get_rounds_by_id(session: Session, num_rounds: int, query_ids: list[int]):
    # Initialize database with round entries
    rounds: list[Round] = []
    for idx in range(num_rounds):
        rnd = Round(
            tee_id=1,
            type=RoundType.FLIGHT,
            scoring_type=ScoringType.INDIVIDUAL,
            date_played=datetime(2024, 1, 1),
            date_updated=datetime.now(),
        )
        session.add(rnd)
        rounds.append(rnd)

    # Get rounds from database
    rounds_db = db_round.get_rounds_by_id(session=session, ids=query_ids)

    # Assert returned rounds are correct based on query
    for round_db in rounds_db:
        assert round_db.id in query_ids
    for query_id in query_ids:
        if query_id <= num_rounds:
            assert any(round_db.id == query_id for round_db in rounds_db)
        else:
            assert all(round_db.id != query_id for round_db in rounds_db)
