r"""
Golf data models

Authors
-------
Andris Jaunzemis

"""

import numpy as np

from usga_handicap import compute_course_handicap, compute_score_differential, compute_adjusted_gross_score

class GolfCourse(object):
    r"""
    Container for 9-hole track on a golf course.

    """

    def __init__(self, course_name, track_name, abbreviation, year_updated, gender, tee_set, tee_color, rating, slope):
        self.course_name = course_name
        self.track_name = track_name
        self.abbreviation = abbreviation
        self.year_updated = year_updated
        self.gender = gender
        self.tee_set = tee_set
        self.tee_color = tee_color
        self.rating = rating
        self.slope = slope
        self.address = None
        self.city = None
        self.state = None
        self.zip_code = None
        self.phone = None
        self.website = None
        self.holes = []
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this course.

        Returns
        -------
        course : dict
            dictionary representation of course data

        """
        return {
            'course_name': self.course_name,
            'track_name': self.track_name,
            'abbreviation': self.abbreviation,
            'year_updated': self.year_updated,
            'gender': self.gender,
            'tee_set': self.tee_set,
            'tee_color': self.tee_color,
            'rating': self.rating,
            'slope': self.slope,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'website': self.website
        }

class GolfHole(object):
    r"""
    Container for a hole from a golf course.

    """

    def __init__(self, number, par, handicap, yardage):
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
            'number': self.number,
            'par': self.par,
            'handicap': self.handicap,
            'yardage': self.yardage
        }
    
class GolfRound(object):
    r"""
    Container for a round played on a golf course.

    """

    def __init__(self, course, player, date_played, player_handicap_index):
        self.course = course
        self.player = player
        self.date_played = date_played
        self.player_handicap_index = player_handicap_index

    def as_dict(self):
        r"""
        Creates dictionary representation of this round.

        """
        return {
            'date_played': self.date_played,
            'player_handicap_index': self.player_handicap_index,
            'player_course_handicap': self.course_handicap,
            'gross_score': self.gross_score,
            'adjusted_gross_score': self.adjusted_gross_score,
            'score_differential': self.score_differential
        }

    @property
    def gross_score(self):
        r"""
        Computes gross score: total number of strokes.

        Returns
        -------
        score : int
            gross score
        
        """
        return np.sum([hole.strokes for hole in self.holes])

    @property
    def adjusted_gross_score(self):
        r"""
        Computes adjusted gross score using course handicap.

        Returns
        -------
        score : int
            adjusted gross score

        """
        return np.sum([compute_adjusted_gross_score(hole.par, hole.handicap, hole.strokes, self.course_handicap) for hole in self.holes])

    @property
    def course_handicap(self):
        r"""
        Computes course handicap using this player's handicap index.

        Returns
        -------
        course_handicap : float
            course handicap for this player

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
