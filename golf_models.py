r"""
Golf data models

Authors
-------
Andris Jaunzemis

"""

import numpy as np
from typing import List

from usga_handicap import compute_course_handicap, compute_score_differential, compute_adjusted_gross_score
    
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
