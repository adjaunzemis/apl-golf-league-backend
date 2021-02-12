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

    def __init__(self, course_name, track_name, abbreviation, tee_name, gender, rating, slope):
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
        return "{:s}: Track={:s}, Tees={:s}, Gender={:s}".format(self.course_name, self.track_name, self.tee_name, self.gender)
    
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
            'tee_name': self.tee_name,
            'gender': self.gender,
            'rating': self.rating,
            'slope': self.slope,
            'tee_color': self.tee_color,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'phone': self.phone,
            'website': self.website
        }

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
        fieldValues = "course_name = '{:s}', track_name = '{:s}', abbreviation = '{:s}', tee_name = '{:s}', gender = '{:s}', rating = {:f}, slope = {:f}".format(self.course_name, self.track_name, self.abbreviation, self.tee_name, self.gender, self.rating, self.slope)

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
        conditions = "course_name = '{:s}' AND track_name = '{:s}' AND tee_name = '{:s}' AND gender = '{:s}'".format(self.course_name, self.track_name, self.tee_name, self.gender)

        # Construct query
        return "UPDATE courses SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_hole(self, number, par, handicap, yardage):
        r"""
        Adds a hole to this golf course.

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
        self.holes.append(GolfHole(number, par, handicap, yardage))

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

    def _create_database_insert_query(self, course_id):
        r"""
        Creates query for inserting this hole into database.

        Parameters
        ----------
        course_id : int
            course identifier from database

        Returns
        -------
        query : string
            database insert query for hole

        """
        # Add required fields
        fields = "course_id, number, par, handicap, yardage"
        values = "{:d}, {:d}, {:d}, {:d}, {:d}".format(course_id, self.number, self.par, self.handicap, self.yardage)

        # Construct query
        return "INSERT INTO course_holes ({:s}) VALUES ({:s})".format(fields, values)

        
    def _create_database_update_query(self, course_id):
        r"""
        Creates query for updating this hole in database.

        Parameters
        ----------
        course_id : int
            course identifier from database

        Returns
        -------
        query : string
            database update query for hole

        """
        # Add required fields
        fieldValues = "number = {:d}, par = {:d}, handicap = {:d}, yardage = {:d}".format(self.number, self.par, self.handicap, self.yardage)

        # Construct conditions
        conditions = "course_id = {:d} AND number = {:d}".format(course_id, self.number)

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
        course : dict
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
