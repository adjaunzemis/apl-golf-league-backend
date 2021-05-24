r"""
Unit test suite for golf course data model

Authors
-------
Andris Jaunzemis

"""

import pytest
from datetime import date

from golf_course import GolfCourse
from golf_track import GolfTrack
from golf_tee_set import GolfTeeSet
from golf_hole import GolfHole

def init_holes(tee_set_id):
    return [
        GolfHole(0, tee_set_id, 1, 4, 1),
        GolfHole(0, tee_set_id, 2, 4, 2),
        GolfHole(0, tee_set_id, 3, 4, 3),
        GolfHole(0, tee_set_id, 4, 4, 4),
        GolfHole(0, tee_set_id, 5, 4, 5),
        GolfHole(0, tee_set_id, 6, 4, 6),
        GolfHole(0, tee_set_id, 7, 4, 7),
        GolfHole(0, tee_set_id, 8, 4, 8),
        GolfHole(0, tee_set_id, 9, 4, 9)
    ]

def init_tee_sets(track_id):
    tee_sets = []
    tee_set_m = GolfTeeSet(0, track_id, "Tee Set", "M", 71.2, 124)
    tee_set_m.color = "ffffff"
    for hole in init_holes(0):
        tee_set_m.add_hole(hole)
    tee_sets.append(tee_set_m)
    tee_set_f = GolfTeeSet(1, track_id, "Tee Set", "F", 72.3, 126)
    tee_set_f.color = "ffffff"
    for hole in init_holes(1):
        tee_set_f.add_hole(hole)
    tee_sets.append(tee_set_f)
    return tee_sets

def init_tracks_valid():
    tracks = []
    track_0 = GolfTrack(0, 0, "Track 0", "T0")
    for tee_set in init_tee_sets(0):
        track_0.add_tee_set(tee_set)
    tracks.append(track_0)
    track_1 = GolfTrack(1, 0, "Track 1", "T1")
    for tee_set in init_tee_sets(1):
        track_1.add_tee_set(tee_set)
    tracks.append(track_1)
    return tracks

def init_tracks_wrong_id():
    tracks = []
    track_0 = GolfTrack(0, 1, "Track 0", "T0")
    for tee_set in init_tee_sets(0):
        track_0.add_tee_set(tee_set)
    tracks.append(track_0)
    track_1 = GolfTrack(1, 1, "Track 1", "T1")
    for tee_set in init_tee_sets(1):
        track_1.add_tee_set(tee_set)
    tracks.append(track_1)
    return tracks

def init_tracks_duplicate():
    tracks = []
    track_0 = GolfTrack(0, 0, "Track 0", "T0")
    for tee_set in init_tee_sets(0):
        track_0.add_tee_set(tee_set)
    tracks.append(track_0)
    track_0dup = GolfTrack(0, 0, "Track 0", "T0")
    for tee_set in init_tee_sets(0):
        track_0dup.add_tee_set(tee_set)
    tracks.append(track_0dup)
    return tracks

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated", [
        (0, "Course", "C", None, None, None, None, None, None, None),
        (0, "Course", "C", "Address", None, None, None, None, None, None),
        (0, "Course", "C", "Address", "City", None, None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today()),
        (None, "Course", "C", None, None, None, None, None, None, None),
        (None, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today())
    ])
def test_constructor(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    assert course.id == id
    assert course.name == name
    assert course.abbreviation == abbreviation
    assert course.address == address
    assert course.city == city
    assert course.state == state
    assert course.zip_code == zip_code
    assert course.phone == phone
    assert course.website == website
    assert course.date_updated == date_updated
    assert len(course.tracks) == 0

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated", [
        (0, "Course", "C", None, None, None, None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today()),
    ])
def test_str(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    assert str(course) == "{:s}".format(name)

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated, init_tracks", [
        (0, "Course", "C", None, None, None, None, None, None, None, init_tracks_valid),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today(), init_tracks_valid),
    ])
def test_add_track(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated, init_tracks):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    tracks = init_tracks()
    for track in tracks:
        course.add_track(track)
    assert len(course.tracks) == len(tracks)
    for track in tracks:
        assert track in course.tracks
        
@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated, init_tracks", [
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today(), init_tracks_wrong_id),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today(), init_tracks_duplicate),
    ])
def test_add_track_errors(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated, init_tracks):
    with pytest.raises(ValueError) as e:
        course = GolfCourse(id, name, abbreviation)
        course.address = address
        course.city = city
        course.state = state
        course.zip_code = zip_code
        course.phone = phone
        course.website = website
        course.date_updated = date_updated
        tracks = init_tracks()
        for track in tracks:
            course.add_track(track)

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated", [
        (0, "Course", "C", None, None, None, None, None, None, None),
        (0, "Course", "C", "Address", None, None, None, None, None, None),
        (0, "Course", "C", "Address", "City", None, None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today()),
        (None, "Course", "C", None, None, None, None, None, None, None),
        (None, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today())
    ])
def test_as_dict(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    course_dict = course.as_dict()
    assert course_dict['id'] == id
    assert course_dict['name'] == name
    assert course_dict['abbreviation'] == abbreviation
    if address is not None:
        assert course_dict['address'] == address
    if city is not None:
        assert course_dict['city'] == city
    if state is not None:
        assert course_dict['state'] == state
    if zip_code is not None:
        assert course_dict['zipCode'] == zip_code
    if phone is not None:
        assert course_dict['phone'] == phone
    if website is not None:
        assert course_dict['website'] == website
    if date_updated is not None:
        assert course_dict['dateUpdated'] == date_updated.strftime("%Y-%m-%d")

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated", [
        (0, "Course", "C", None, None, None, None, None, None, None),
        (0, "Course", "C", "Address", None, None, None, None, None, None),
        (0, "Course", "C", "Address", "City", None, None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today()),
        (None, "Course", "C", None, None, None, None, None, None, None),
        (None, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today())
    ])
def test_create_database_insert_query(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    query = course._create_database_insert_query()
    fields = "name, abbreviation"
    values = "'{:s}', '{:s}'".format(name, abbreviation)
    if address is not None:
        fields += ", address"
        values += ", '{:s}'".format(address)
    if city is not None:
        fields += ", city"
        values += ", '{:s}'".format(city)
    if state is not None:
        fields += ", state"
        values += ", '{:s}'".format(state)
    if zip_code is not None:
        fields += ", zip_code"
        values += ", {:d}".format(zip_code)
    if phone is not None:
        fields += ", phone"
        values += ", '{:s}'".format(phone)
    if website is not None:
        fields += ", website"
        values += ", '{:s}'".format(website)
    assert query == "INSERT INTO courses ({:s}) VALUES ({:s});".format(fields, values)

@pytest.mark.parametrize(
    "id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated", [
        (0, "Course", "C", None, None, None, None, None, None, None),
        (0, "Course", "C", "Address", None, None, None, None, None, None),
        (0, "Course", "C", "Address", "City", None, None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", None, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, None, None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", None, None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", None),
        (0, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today()),
        (None, "Course", "C", None, None, None, None, None, None, None),
        (None, "Course", "C", "Address", "City", "ST", 12345, "123-456-7890", "google.com", date.today())
    ])
def test_create_database_update_query(id, name, abbreviation, address, city, state, zip_code, phone, website, date_updated):
    course = GolfCourse(id, name, abbreviation)
    if address is not None:
        course.address = address
    if city is not None:
        course.city = city
    if state is not None:
        course.state = state
    if zip_code is not None:
        course.zip_code = zip_code
    if phone is not None:
        course.phone = phone
    if website is not None:
        course.website = website
    if date_updated is not None:
        course.date_updated = date_updated
    query = course._create_database_update_query()
    fieldValues = "name = '{:s}', abbreviation = '{:s}'".format(name, abbreviation)
    if address is not None:
        fieldValues += ", address = '{:s}'".format(address)
    if city is not None:
        fieldValues += ", city = '{:s}'".format(city)
    if state is not None:
        fieldValues += ", state = '{:s}'".format(state)
    if zip_code is not None:
        fieldValues += ", zip_code = '{:d}'".format(zip_code)
    if phone is not None:
        fieldValues += ", phone = '{:s}'".format(phone)
    if website is not None:
        fieldValues += ", website = '{:s}'".format(website)
    if id is not None:
        conditions = "id = {:d}".format(id)
    else:
        conditions = "name = '{:s}'".format(name)
    assert query == "UPDATE courses SET {:s} WHERE {:s};".format(fieldValues, conditions)
