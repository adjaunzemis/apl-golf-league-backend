from datetime import datetime, timedelta
from random import random

import pytest
from sqlmodel import Session

from app.database import handicap as db_handicap
from app.models.handicap import HandicapIndex


def generate_random_number(min_value: float = -5, max_value: float = 36):
    """Generates a random number within the given range."""
    return random() * (max_value - min_value) + min_value


@pytest.mark.parametrize("num_rounds", [0, 1, 5, 10, 20, 30, 40, 50, 100])
def test_get_handicap_history_for_golfer(session: Session, num_rounds: int):
    # Initialize database with handicap entries
    GOLFER_ID = 1
    handicaps: list[HandicapIndex] = []
    for idx in range(num_rounds):
        hcp = HandicapIndex(
            golfer_id=GOLFER_ID,
            date_posted=datetime.now() - timedelta(days=(num_rounds - idx)),
            round_number=1,
            handicap_index=generate_random_number(),
        )
        session.add(hcp)
        handicaps.append(hcp)

    # Get handicap data from database
    handicaps_db = db_handicap.get_handicap_history_for_golfer(
        session=session, golfer_id=GOLFER_ID
    )

    # Assert return values are correct length, complete, and in expected order
    assert len(handicaps_db) == num_rounds
    assert all(
        [
            handicaps_db[-1].date_posted >= hcp_db.date_posted
            for hcp_db in handicaps_db[:-1]
        ]
    )
    for hcp in handicaps:
        assert hcp.date_posted in [hcp_db.date_posted for hcp_db in handicaps_db]
        assert hcp.handicap_index in [hcp_db.handicap_index for hcp_db in handicaps_db]
