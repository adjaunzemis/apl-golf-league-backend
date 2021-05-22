r"""
Unit test suite for golf hole data model

Authors
-------
Andris Jaunzemis

"""

import pytest

from golf_hole import GolfHole

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap", [
        (0, 1, 2, 3, 4)
    ])
def test_constructor(id, tee_set_id, number, par, handicap):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    assert hole.id == id
    assert hole.tee_set_id == tee_set_id
    assert hole.number == number
    assert hole.par == par
    assert hole.handicap == handicap
    assert hole.yardage is None

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (0, 1, 2, 3, 4, 123)
    ])
def test_hole_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    assert hole.id == id
    assert hole.tee_set_id == tee_set_id
    assert hole.number == number
    assert hole.par == par
    assert hole.handicap == handicap
    assert hole.yardage == yardage
    
@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap", [
        (0, 1, 2, 3, 4)
    ])
def test_str(id, tee_set_id, number, par, handicap):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    assert str(hole) == "{:d} (Par={:d}, Handicap={:d}, Yardage=n/a)".format(number, par, handicap)
    
@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (0, 1, 2, 3, 4, 123)
    ])
def test_str_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    assert str(hole) == "{:d} (Par={:d}, Handicap={:d}, Yardage={:d})".format(number, par, handicap, yardage)

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap", [
        (0, 1, 2, 3, 4)
    ])
def test_as_dict(id, tee_set_id, number, par, handicap):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole_dict = hole.as_dict()
    assert hole_dict['id'] == id
    assert hole_dict['teeSetId'] == tee_set_id
    assert hole_dict['number'] == number
    assert hole_dict['par'] == par
    assert hole_dict['handicap'] == handicap
    assert hole_dict.get('yardage') is None

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (0, 1, 2, 3, 4, 123)
    ])
def test_as_dict_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    hole_dict = hole.as_dict()
    assert hole_dict['id'] == id
    assert hole_dict['teeSetId'] == tee_set_id
    assert hole_dict['number'] == number
    assert hole_dict['par'] == par
    assert hole_dict['handicap'] == handicap
    assert hole_dict['yardage'] == yardage

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap", [
        (0, 1, 2, 3, 4)
    ])
def test_create_database_insert_query(id, tee_set_id, number, par, handicap):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    query = hole._create_database_insert_query()
    fields = "tee_set_id, number, par, handicap"
    values = "{:d}, {:d}, {:d}, {:d}".format(tee_set_id, number, par, handicap)
    assert query == "INSERT INTO holes ({:s}) VALUES ({:s});".format(fields, values)

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (0, 1, 2, 3, 4, 123)
    ])
def test_create_database_insert_query_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    query = hole._create_database_insert_query()
    fields = "tee_set_id, number, par, handicap, yardage"
    values = "{:d}, {:d}, {:d}, {:d}, {:d}".format(tee_set_id, number, par, handicap, yardage)
    assert query == "INSERT INTO holes ({:s}) VALUES ({:s});".format(fields, values)

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (0, 1, 2, 3, 4, 123)
    ])
def test_create_database_update_query_with_id_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    query = hole._create_database_update_query()
    fieldValues = "tee_set_id = {:d}, number = {:d}, par = {:d}, handicap = {:d}, yardage = {:d}".format(tee_set_id, number, par, handicap, yardage)
    conditions = "id = {:d}".format(id)
    assert query == "UPDATE holes SET {:s} WHERE {:s};".format(fieldValues, conditions)

@pytest.mark.parametrize(
    "id, tee_set_id, number, par, handicap, yardage", [
        (None, 1, 2, 3, 4, 123)
    ])
def test_create_database_update_query_without_id_with_optional_fields(id, tee_set_id, number, par, handicap, yardage):
    hole = GolfHole(id, tee_set_id, number, par, handicap)
    hole.yardage = yardage
    query = hole._create_database_update_query()
    fieldValues = "tee_set_id = {:d}, number = {:d}, par = {:d}, handicap = {:d}, yardage = {:d}".format(tee_set_id, number, par, handicap, yardage)
    conditions = "tee_set_id = {:d} AND number = {:d}".format(tee_set_id, number)
    assert query == "UPDATE holes SET {:s} WHERE {:s};".format(fieldValues, conditions)
