r"""
Unit test suite for golf tee set data model

Authors
-------
Andris Jaunzemis

"""

import pytest

from golf_tee_set import GolfTeeSet
from golf_hole import GolfHole

def init_holes_valid():
    return [
        GolfHole(0, 0, 1, 4, 1),
        GolfHole(0, 0, 2, 4, 2),
        GolfHole(0, 0, 3, 4, 3),
        GolfHole(0, 0, 4, 4, 4),
        GolfHole(0, 0, 5, 4, 5),
        GolfHole(0, 0, 6, 4, 6),
        GolfHole(0, 0, 7, 4, 7),
        GolfHole(0, 0, 8, 4, 8),
        GolfHole(0, 0, 9, 4, 9)
    ]

def init_holes_wrong_id():
    return [
        GolfHole(0, 1, 1, 4, 1)
    ]

def init_holes_duplicate():
    return [
        GolfHole(0, 0, 1, 4, 1),
        GolfHole(0, 0, 1, 4, 1)
    ]

def init_tee_set(id, track_id, name, gender, rating, slope, color):
    tee_set = GolfTeeSet(id, track_id, name, gender, rating, slope)
    if color is not None:
        tee_set.color = color
    return tee_set

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color", [
        (0, 0, "Tee Set", "M", 71.2, 124, None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff"),
        (None, 0, "Tee Set", "M", 71.2, 124, None),
        (None, 0, "Tee Set", "M", 71.2, 124, "ffffff")
    ])
def test_constructor(id, track_id, name, gender, rating, slope, color):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    assert tee_set.id == id
    assert tee_set.track_id == track_id
    assert tee_set.name == name
    assert tee_set.gender == gender
    assert tee_set.rating == rating
    assert tee_set.slope == slope
    assert tee_set.color == color
    assert len(tee_set.holes) == 0

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color", [
        (0, 0, "Tee Set", "M", 71.2, 124, None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff"),
        (None, 0, "Tee Set", "M", 71.2, 124, None),
        (None, 0, "Tee Set", "M", 71.2, 124, "ffffff")
    ])
def test_str(id, track_id, name, gender, rating, slope, color):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    assert str(tee_set) == "{:s} ({:s}: {:.1f}/{:.1f})".format(name, gender, rating, slope)

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color, init_holes", [
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_valid),
    ])
def test_add_hole(id, track_id, name, gender, rating, slope, color, init_holes):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    holes = init_holes()
    for hole in holes:
        tee_set.add_hole(hole)
    assert len(tee_set.holes) == len(holes)
    for hole in holes:
        assert hole in tee_set.holes

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color, init_holes", [
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_wrong_id),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_duplicate)
    ])
def test_add_hole_errors(id, track_id, name, gender, rating, slope, color, init_holes):
    with pytest.raises(ValueError) as e:
        tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
        holes = init_holes()
        for hole in holes:
            tee_set.add_hole(hole)

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color, init_holes", [
        (0, 0, "Tee Set", "M", 71.2, 124, None, None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (None, 0, "Tee Set", "M", 71.2, 124, None, None),
        (None, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_valid),
    ])
def test_as_dict(id, track_id, name, gender, rating, slope, color, init_holes):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    holes = None
    if init_holes is not None:
        holes = init_holes()
    if holes is not None:
        for hole in holes:
            tee_set.add_hole(hole)
    tee_set_dict = tee_set.as_dict()
    assert tee_set_dict['id'] == id
    assert tee_set_dict['trackId'] == track_id
    assert tee_set_dict['name'] == name
    assert tee_set_dict['gender'] == gender
    assert tee_set_dict['rating'] == rating
    assert tee_set_dict['slope'] == slope
    if color is not None:
        assert tee_set_dict['color'] == color
    else:
        assert tee_set_dict.get('color') is None
    if holes is None:
        assert len(tee_set_dict['holes']) == 0
    else:
        assert len(tee_set_dict['holes']) == len(holes)
        for hole in holes:
            assert hole.as_dict() in tee_set_dict['holes']

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color, init_holes", [
        (0, 0, "Tee Set", "M", 71.2, 124, None, None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (None, 0, "Tee Set", "M", 71.2, 124, None, None),
        (None, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_valid),
    ])
def test_create_database_insert_query(id, track_id, name, gender, rating, slope, color, init_holes):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    holes = None
    if init_holes is not None:
        holes = init_holes()
    if holes is not None:
        for hole in holes:
            tee_set.add_hole(hole)
    query = tee_set._create_database_insert_query()
    fields = "track_id, name, gender, rating, slope"
    values = "{:d}, '{:s}', '{:s}', {:f}, {:f}".format(track_id, name, gender, rating, slope)
    if color is not None:
        fields += ", color"
        values += ", '{:s}'".format(color)
    assert query == "INSERT INTO tee_sets ({:s}) VALUES ({:s});".format(fields, values)

@pytest.mark.parametrize(
    "id, track_id, name, gender, rating, slope, color, init_holes", [
        (0, 0, "Tee Set", "M", 71.2, 124, None, None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (None, 0, "Tee Set", "M", 71.2, 124, None, None),
        (None, 0, "Tee Set", "M", 71.2, 124, "ffffff", None),
        (0, 0, "Tee Set", "M", 71.2, 124, "ffffff", init_holes_valid),
    ])
def test_create_database_update_query(id, track_id, name, gender, rating, slope, color, init_holes):
    tee_set = init_tee_set(id, track_id, name, gender, rating, slope, color)
    holes = None
    if init_holes is not None:
        holes = init_holes()
    if holes is not None:
        for hole in holes:
            tee_set.add_hole(hole)
    query = tee_set._create_database_update_query()
    fieldValues = "track_id = {:d}, name = '{:s}', gender = '{:s}', rating = {:f}, slope = {:f}".format(track_id, name, gender, rating, slope)
    if color is not None:
        fieldValues += ", color = '{:s}'".format(color)
    if id is not None:
        conditions = "id = {:d}".format(id)
    else:
        conditions = "track_id = {:d} AND name = '{:s}' AND gender = '{:s}'".format(track_id, name, gender)
    assert query == "UPDATE tee_sets SET {:s} WHERE {:s};".format(fieldValues, conditions)
