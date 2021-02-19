r"""
Golf data models

Authors
-------
Andris Jaunzemis

"""

import numpy as np
from typing import List

from usga_handicap import compute_course_handicap, compute_score_differential, compute_adjusted_gross_score

class GolfCourse(object):
    r"""
    Container for 9-hole track on a golf course.

    """

    def __init__(self, id, course_name, track_name, abbreviation, tee_name, gender, rating, slope):
        self.id = id
        self.course_name = course_name
        self.track_name = track_name
        self.abbreviation = abbreviation
        self.tee_name = tee_name
        self.gender = gender
        self.rating = rating
        self.slope = slope
        self.tee_color = None
        self.address = None
        self.city = None
        self.state = None
        self.zip_code = None
        self.phone = None
        self.website = None
        self.holes = []

    def __str__(self):
        r"""
        Customizes string representation for GolfCourse objects.

        Returns
        -------
        s : string
            string representation of GolfCourse

        """
        return "{:s} (id={:d}, track_name={:s}, tee_name={:s}, gender={:s})".format(self.course_name, self.id, self.track_name, self.tee_name, self.gender)
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this course.

        Returns
        -------
        course_dict : dict
            dictionary representation of course data

        """
        # Add required fields.
        course_dict = {
            'id': self.id,
            'courseName': self.course_name,
            'trackName': self.track_name,
            'teeName': self.tee_name,
            'gender': self.gender,
            'rating': self.rating,
            'slope': self.slope,
            'holes': [hole.as_dict() for hole in self.holes],
            'par': self.par
        }

        # Add optional fields if defined.
        if self.abbreviation is not None:
            course_dict['abbreviation'] = self.abbreviation
        if self.tee_color is not None:
            course_dict['teeColor'] = self.tee_color
        if self.address is not None:
            course_dict['address'] = self.address
        if self.city is not None:
            course_dict['city'] = self.city
        if self.state is not None:
            course_dict['state'] = self.state
        if self.zip_code is not None:
            course_dict['zipCode'] = self.zip_code
        if self.phone is not None:
            course_dict['phone'] = self.phone
        if self.website is not None:
            course_dict['website'] = self.website

        # Return dictionary.
        return course_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this course into database.

        Returns
        -------
        query : string
            database insert query for course

        """
        # Add required fields
        fields = "course_name, track_name, abbreviation, tee_name, gender, rating, slope"
        values = "'{:s}', '{:s}', '{:s}', '{:s}', '{:s}', {:f}, {:f}".format(self.course_name, self.track_name, self.abbreviation, self.tee_name, self.gender, self.rating, self.slope)

        # Add optional fields if defined
        if self.tee_color is not None:
            fields += ", tee_color"
            values += ", '{:s}'".format(self.tee_color)
        if self.address is not None:
            fields += ", address"
            values += ", '{:s}'".format(self.address)
        if self.city is not None:
            fields += ", city"
            values += ", '{:s}'".format(self.city)
        if self.state is not None:
            fields += ", state"
            values += ", '{:s}'".format(self.state)
        if self.zip_code is not None:
            fields += ", zip_code"
            values += ", {:d}".format(self.zip_code)
        if self.phone is not None:
            fields += ", phone"
            values += ", '{:s}'".format(self.phone)
        if self.website is not None:
            fields += ", website"
            values += ", '{:s}'".format(self.website)

        # Construct query
        return "INSERT INTO courses ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this course in database.

        Returns
        -------
        query : string
            database update query for course

        """
        # Add required fields
        fieldValues = "id = {:d}, course_name = '{:s}', track_name = '{:s}', abbreviation = '{:s}', tee_name = '{:s}', gender = '{:s}', rating = {:f}, slope = {:f}".format(self.id, self.course_name, self.track_name, self.abbreviation, self.tee_name, self.gender, self.rating, self.slope)

        # Add optional fields if defined
        if self.tee_color is not None:
            fieldValues += ", tee_color = '{:s}'".format(self.tee_color)
        if self.address is not None:
            fieldValues += ", address = '{:s}'".format(self.address)
        if self.city is not None:
            fieldValues += ", city = '{:s}'".format(self.city)
        if self.state is not None:
            fieldValues += ", state = '{:s}'".format(self.state)
        if self.zip_code is not None:
            fieldValues += ", zip_code = '{:s}'".format(self.zip_code)
        if self.phone is not None:
            fieldValues += ", phone = '{:s}'".format(self.phone)
        if self.website is not None:
            fieldValues += ", website = '{:s}'".format(self.website)

        # Construct conditions
        if self.id is not None:
            conditions = "id = {:d}".format(self.id)
        else:
            conditions = "course_name = '{:s}' AND track_name = '{:s}' AND tee_name = '{:s}' AND gender = '{:s}'".format(self.course_name, self.track_name, self.tee_name, self.gender)

        # Construct query
        return "UPDATE courses SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_hole(self, hole):
        r"""
        Add a hole to this golf course.

        Parameters
        ----------
        hole : GolfHole
            hole to add

        Raises
        ------
        ValueError :
            if course identifier for given hole does not match this course identifier
            if this course already contains a hole with the given number
        
        """
        if hole.course_id != self.id:
            raise ValueError("Cannot add hole with course id={:d} to course with id={:d}".format(hole.course_id, self.id))
        if hole.number in [h.number for h in self.holes]:
            raise ValueError("Course (id={:d}) already contains a hole with number={:d}".format(self.id, hole.number))
        self.holes.append(hole)

    def create_hole(self, number, par, handicap, yardage):
        r"""
        Creates a golf hole using the given data and adds it to this golf course.

        Parameters
        ----------
        number : int
            hole number
        par : int
            hole par
        handicap : int
            hole handicap
        yardage : int
            hole yardage

        """
        self.add_hole(GolfHole(self.id, number, par, handicap, yardage))

    @property
    def par(self):
        r"""
        Computes total par for this course.

        Returns
        -------
        par : int
            par for this course
        
        """
        return np.sum([hole.par for hole in self.holes])

class GolfHole(object):
    r"""
    Container for a hole from a golf course.

    """

    def __init__(self, course_id, number, par, handicap, yardage):
        self.course_id = course_id
        self.number = number
        self.par = par
        self.handicap = handicap
        self.yardage = yardage

    def as_dict(self):
        r"""
        Creates dictionary representation of this hole.

        Returns
        -------
        hole : dict
            dictionary representation of hole data
        
        """
        return {
            'courseID': self.course_id,
            'number': self.number,
            'par': self.par,
            'handicap': self.handicap,
            'yardage': self.yardage
        }

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this hole into database.

        Returns
        -------
        query : string
            database insert query for hole

        """
        # Add required fields
        fields = "course_id, number, par, handicap, yardage"
        values = "{:d}, {:d}, {:d}, {:d}, {:d}".format(self.course_id, self.number, self.par, self.handicap, self.yardage)

        # Construct query
        return "INSERT INTO course_holes ({:s}) VALUES ({:s})".format(fields, values)
        
    def _create_database_update_query(self):
        r"""
        Creates query for updating this hole in database.

        Returns
        -------
        query : string
            database update query for hole

        """
        # Add required fields
        fieldValues = "number = {:d}, par = {:d}, handicap = {:d}, yardage = {:d}".format(self.number, self.par, self.handicap, self.yardage)

        # Construct conditions
        conditions = "course_id = {:d} AND number = {:d}".format(self.course_id, self.number)

        # Construct query
        return "UPDATE course_holes SET {:s} WHERE {:s};".format(fieldValues, conditions)
    
class GolfHoleResult(object):
    r"""
    Container for a result on a given golf hole.

    """

    def __init__(self, hole, strokes):
        self.hole = hole
        self.strokes = strokes

class GolfRound(object):
    r"""
    Container for a round played on a golf course.

    """

    def __init__(self, course, player, date_played, player_handicap_index):
        self.course = course
        self.player = player
        self.date_played = date_played
        self.player_handicap_index = player_handicap_index
        self.hole_results = []

    def as_dict(self):
        r"""
        Creates dictionary representation of this round.

        Returns
        -------
        course : dict
            dictionary representation of round data

        """
        return {
            'date_played': self.date_played,
            'player_handicap_index': self.player_handicap_index,
            'player_course_handicap': self.course_handicap,
            'gross_score': self.gross_score,
            'adjusted_gross_score': self.adjusted_gross_score,
            'score_differential': self.score_differential
        }
    
    def add_hole_score(self, number, strokes):
        r"""
        Adds number of strokes taken on a hole for this round.

        Parameters
        ----------
        number : int
            hole number
        strokes : int
            number of strokes taken on this hole
        
        """
        holeMatch = None
        for hole in self.course.holes:
            if hole.number == number:
                holeMatch = hole
                break

        if holeMatch is None:
            raise Exception('Unable to find match for hole number {:d}'.format(number))
        self.hole_results.append(GolfHoleResult(holeMatch, strokes))

    @property
    def gross_score(self):
        r"""
        Computes gross score: total number of strokes.

        Returns
        -------
        score : int
            gross score
        
        """
        return np.sum([hole.strokes for hole in self.hole_results])

    @property
    def adjusted_gross_score(self):
        r"""
        Computes adjusted gross score using course handicap index.

        Returns
        -------
        score : int
            adjusted gross score

        """
        return np.sum([compute_adjusted_gross_score(hole_result.hole.par, hole_result.hole.handicap, hole_result.strokes, self.course_handicap) for hole_result in self.hole_results])

    @property
    def course_handicap(self):
        r"""
        Computes course handicap index using player's handicap index.

        Returns
        -------
        handicap : float
            course handicap index for this player

        """
        return compute_course_handicap(self.course.par, self.course.rating, self.course.slope, self.player_handicap_index)

    @property
    def score_differential(self):
        r"""
        Computes score differential.

        Returns
        -------
        score_differential : float
            score differential
        
        """
        return compute_score_differential(self.course.rating, self.course.slope, self.adjusted_gross_score)

class GolfFlight(object):
    r"""
    Container for golf league flight information.

    """

    def __init__(self, name, year, abbreviation, mens_course_id, senior_course_id, super_senior_course_id, womens_course_id):
        self.name = name
        self.year = year
        self.abbreviation = abbreviation
        self.mens_course_id = mens_course_id
        self.senior_course_id = senior_course_id
        self.super_senior_course_id = super_senior_course_id
        self.womens_course_id = womens_course_id

    def __str__(self):
        r"""
        Creates string representation of golf flight information.

        Returns
        -------
        s : string
            string representation of flight information
        
        """
        return "{:s} ({:d})".format(self.name, self.year)

    def as_dict(self):
        r"""
        Creates dictionary representation of golf league flight information.

        Returns
        -------
        flight : dict
            dictionary representation of golf league flight information
        
        """
        return {
            'name': self.name,
            'year': self.year,
            'abbreviation': self.abbreviation,
            'mens_course_id': self.mens_course_id,
            'senior_course_id': self.senior_course_id,
            'super_senior_course_id': self.super_senior_course_id,
            'womens_course_id': self.womens_course_id
        }

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this flight into database.

        Returns
        -------
        query : string
            database insert query for flight

        """
        # Add required fields
        fields = "name, year, abbreviation, mens_course_id, senior_course_id, super_senior_course_id, womens_course_id"
        values = "'{:s}', {:d}, '{:s}', {:d}, {:d}, {:d}, {:d}".format(self.name, self.year, self.abbreviation, self.mens_course_id, self.senior_course_id, self.super_senior_course_id, self.womens_course_id)

        # Construct query
        return "INSERT INTO flights ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self, flight_id):
        r"""
        Creates query for updating this flight in database.

        Parameters
        ----------
        flight_id : int
            flight identifier in database

        Returns
        -------
        query : string
            database update query for flight

        """
        # Add required fields
        fieldValues = "name = '{:s}', year = {:d}, abbreviation = '{:s}', mens_course_id = {:d}, senior_course_id = {:d}, super_senior_course_id = {:d}, womens_course_id = {:d}".format(self.name, self.year, self.abbreviation, self.mens_course_id, self.senior_course_id, self.super_senior_course_id, self.womens_course_id)

        # Construct conditions
        conditions = "id = {:d}".format(flight_id)

        # Construct query
        return "UPDATE flights SET {:s} WHERE {:s};".format(fieldValues, conditions)

class GolfPlayer(object):
    r"""
    Container for golf player information.

    """
    
    def __init__(self, first_name, last_name, classification, email):
        self.first_name = first_name
        self.last_name = last_name
        self.classification = classification
        self.email = email
        self.phone = None
        self.location = None
        self.employee_id = None

    def __str__(self):
        r"""
        Creates string representation of this player.

        Returns
        -------
        s : string
            string representation of player information
        
        """
        return "{:s} {:s}".format(self.first_name, self.last_name)
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this player.

        Returns
        -------
        player : dict
            dictionary representation of player information

        """
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'classification': self.classification,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'employee_id': self.employee_id
        }

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this player into database.

        Returns
        -------
        query : string
            database insert query for player

        """
        # Add required fields
        fields = "first_name, last_name, classification, email"
        values = "'{:s}', '{:s}', '{:s}', '{:s}'".format(self.first_name, self.last_name, self.classification, self.email)

        # Add optional fields if defined
        if self.phone is not None:
            fields += ", phone"
            values += ", '{:s}'".format(self.phone)
        if self.location is not None:
            fields += ", location"
            values += ", '{:s}'".format(self.location)
        if self.employee_id is not None:
            fields += ", employee_id"
            values += ", '{:s}'".format(self.employee_id)

        # Construct query
        return "INSERT INTO players ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self, player_id):
        r"""
        Creates query for updating this player in database.

        Parameters
        ----------
        player_id : int
            player identifier in database

        Returns
        -------
        query : string
            database update query for player

        """
        # Add required fields
        fieldValues = "first_name = '{:s}', last_name = '{:s}', classification = '{:s}', email = '{:s}'".format(self.first_name, self.last_name, self.classification, self.email)

        # Add optional fields if defined
        if self.phone is not None:
            fieldValues += ", phone = '{:s}'".format(self.phone)
        if self.location is not None:
            fieldValues += ", location = '{:s}'".format(self.location)
        if self.employee_id is not None:
            fieldValues += ", employee_id = '{:s}'".format(self.employee_id)

        # Construct conditions
        conditions = "id = {:d}".format(player_id)

        # Construct query
        return "UPDATE players SET {:s} WHERE {:s};".format(fieldValues, conditions)

class GolfTeam(object):
    r"""
    Container class for golf league team.

    """

    def __init__(self, flight: GolfFlight, number: int, players: List[GolfPlayer]):
        self.flight = flight
        self.number = number
        self.players = players
        self.name = None
    
    def __str__(self):
        r"""
        Creates string representation of this team.

        Returns
        -------
        s : string
            string representation of team information

        """
        return "{:s} Team {:d}".format(str(self.flight), self.number)

    def as_dict(self):
        r"""
        Create dictionary representation of this team.

        Returns
        -------
        d : dict
            dictionary representation of team information

        """
        return {
            'flight_name': str(self.flight),
            'number': self.number,
            'name': self.name,
            'player_names': [player.first_name + player.last_name for player in self.players]
        }

    def _create_database_insert_query(self, flight_id: int):
        r"""
        Creates query for inserting this team into database.

        Parameters
        ----------
        flight_id : int
            flight identifier in database

        Returns
        -------
        query : string
            database insert query for team

        """
        # Add required fields
        fields = "flight_id, number"
        values = "{:d}, {:d}, '{:s}'".format(flight_id, self.number)

        # Add optional fields if defined
        if self.name is not None:
            fields += ", name"
            values += ", '{:s}'".format(self.name)

        # Construct query
        return "INSERT INTO teams ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self, team_id: int, flight_id: int):
        r"""
        Creates query for updating this team in database.

        Parameters
        ----------
        team_id : int
            team identifier in database
        flight_id : int
            flight identifier in database

        Returns
        -------
        query : string
            database update query for team

        """
        # Add required fields
        fieldValues = "flight_id = {:d}, number = {:d}".format(flight_id, self.number)

        # Add optional fields if defined
        if self.name is not None:
            fieldValues += ", name = '{:s}'".format(self.name)

        # Construct conditions
        conditions = "id = {:d}".format(team_id)

        # Construct query
        return "UPDATE teams SET {:s} WHERE {:s};".format(fieldValues, conditions)
