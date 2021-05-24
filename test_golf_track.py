r"""
Unit test suite for golf track data model

Authors
-------
Andris Jaunzemis

"""

import pytest

from golf_track import GolfTrack
from golf_tee_set import GolfTeeSet
from golf_hole import GolfHole

def init_holes():
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

def init_tee_sets_valid():
    tee_sets = []
    tee_set_m = GolfTeeSet(0, 0, "Tee Set", "M", 71.2, 124)
    tee_set_m.color = "ffffff"
    for hole in init_holes():
        tee_set_m.add_hole(hole)
    tee_sets.append(tee_set_m)
    tee_set_f = GolfTeeSet(0, 0, "Tee Set", "F", 72.3, 126)
    tee_set_f.color = "ffffff"
    for hole in init_holes():
        tee_set_f.add_hole(hole)
    tee_sets.append(tee_set_f)
    return tee_sets

def init_tee_sets_wrong_id():
    tee_sets = []
    tee_set_m = GolfTeeSet(0, 1, "Tee Set", "M", 71.2, 124)
    tee_set_m.color = "ffffff"
    for hole in init_holes():
        tee_set_m.add_hole(hole)
    tee_sets.append(tee_set_m)
    return tee_sets

def init_tee_sets_duplicate():
    tee_sets = []
    tee_set_m = GolfTeeSet(0, 0, "Tee Set", "M", 71.2, 124)
    tee_set_m.color = "ffffff"
    for hole in init_holes():
        tee_set_m.add_hole(hole)
    tee_sets.append(tee_set_m)
    tee_set_m2 = GolfTeeSet(0, 0, "Tee Set", "M", 72.3, 126)
    tee_set_m2.color = "ffffff"
    for hole in init_holes():
        tee_set_m2.add_hole(hole)
    tee_sets.append(tee_set_m2)
    return tee_sets

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation", [
        (0, 0, "Track", "T"),
        (None, 0, "Track", "T")
    ])
def test_constructor(id, course_id, name, abbreviation):
    track = GolfTrack(id, course_id, name, abbreviation)
    assert track.id == id
    assert track.course_id == course_id
    assert track.name == name
    assert track.abbreviation == abbreviation
    assert len(track.tee_sets) == 0

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation", [
        (0, 0, "Track", "T"),
        (None, 0, "Track", "T")
    ])
def test_str(id, course_id, name, abbreviation):
    track = GolfTrack(id, course_id, name, abbreviation)
    assert str(track) == "{:s}".format(name)

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation, init_tee_sets", [
        (0, 0, "Track", "T", init_tee_sets_valid)
    ])
def test_add_tee_set(id, course_id, name, abbreviation, init_tee_sets):
    track = GolfTrack(id, course_id, name, abbreviation)
    tee_sets = init_tee_sets()
    for tee_set in tee_sets:
        track.add_tee_set(tee_set)
    assert track.id == id
    assert track.course_id == course_id
    assert track.name == name
    assert track.abbreviation == abbreviation
    assert len(track.tee_sets) == len(tee_sets)
    for tee_set in tee_sets:
        assert tee_set in track.tee_sets

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation, init_tee_sets", [
        (0, 0, "Track", "T", init_tee_sets_wrong_id),
        (0, 0, "Track", "T", init_tee_sets_duplicate)
    ])
def test_add_tee_set_errors(id, course_id, name, abbreviation, init_tee_sets):
    with pytest.raises(ValueError) as e:
        track = GolfTrack(id, course_id, name, abbreviation)
        tee_sets = init_tee_sets()
        for tee_set in tee_sets:
            track.add_tee_set(tee_set)

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation, init_tee_sets", [
        (0, 0, "Track", "T", None),
        (0, 0, "Track", "T", init_tee_sets_valid),
        (None, 0, "Track", "T", None)
    ])
def test_as_dict(id, course_id, name, abbreviation, init_tee_sets):
    track = GolfTrack(id, course_id, name, abbreviation)
    tee_sets = None
    if init_tee_sets is not None:
        tee_sets = init_tee_sets()
    if tee_sets is not None:
        for tee_set in tee_sets:
            track.add_tee_set(tee_set)
    track_dict = track.as_dict()
    assert track_dict['id'] == id
    assert track_dict['courseId'] == course_id
    assert track_dict['name'] == name
    assert track_dict['abbreviation'] == abbreviation
    if tee_sets is None:
        assert len(track_dict['teeSets']) == 0
    else:
        assert len(track_dict['teeSets']) == len(tee_sets)
        for tee_set in tee_sets:
            assert tee_set.as_dict() in track_dict['teeSets']

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation, init_tee_sets", [
        (0, 0, "Track", "T", None),
        (0, 0, "Track", "T", init_tee_sets_valid),
        (None, 0, "Track", "T", None)
    ])
def test_create_database_insert_query(id, course_id, name, abbreviation, init_tee_sets):
    track = GolfTrack(id, course_id, name, abbreviation)
    tee_sets = None
    if init_tee_sets is not None:
        tee_sets = init_tee_sets()
    if tee_sets is not None:
        for tee_set in tee_sets:
            track.add_tee_set(tee_set)
    query = track._create_database_insert_query()
    fields = "course_id, name, abbreviation"
    values = "{:d}, '{:s}', '{:s}'".format(course_id, name, abbreviation)
    assert query == "INSERT INTO tracks ({:s}) VALUES ({:s});".format(fields, values)

@pytest.mark.parametrize(
    "id, course_id, name, abbreviation, init_tee_sets", [
        (0, 0, "Track", "T", None),
        (0, 0, "Track", "T", init_tee_sets_valid),
        (None, 0, "Track", "T", None)
    ])
def test_create_database_update_query(id, course_id, name, abbreviation, init_tee_sets):
    track = GolfTrack(id, course_id, name, abbreviation)
    tee_sets = None
    if init_tee_sets is not None:
        tee_sets = init_tee_sets()
    if tee_sets is not None:
        for tee_set in tee_sets:
            track.add_tee_set(tee_set)
    query = track._create_database_update_query()
    fieldValues = "course_id = {:d}, name = '{:s}', abbreviation = '{:s}'".format(course_id, name, abbreviation)
    if id is not None:
        conditions = "id = {:d}".format(id)
    else:
        conditions = "course_id = {:d} AND name = '{:s}'".format(course_id, name)
    assert query == "UPDATE tracks SET {:s} WHERE {:s};".format(fieldValues, conditions)
