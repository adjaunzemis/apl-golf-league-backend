r"""
Unit test suite for golf tee set data model

Authors
-------
Andris Jaunzemis

"""

import pytest

from golf_tee_set import GolfTeeSet

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color", [
        (0, 1, "Tee Set", "M", 71.2, 124, None),
        (0, 1, "Tee Set", "M", 71.2, 124, "ffffff")
    ])
def test_constructor(id, track_id, name, gender, rating, slope, color):
    tee_set = GolfTeeSet(id, track_id, name, gender, rating, slope)
    if color is not None:
        tee_set.color = color
    assert tee_set.id == id
    assert tee_set.track_id == track_id
    assert tee_set.name == name
    assert tee_set.gender == gender
    assert tee_set.rating == rating
    assert tee_set.slope == slope
    assert tee_set.color == color
    assert len(tee_set.holes) == 0
