r"""
Golf track data model

Authors
-------
Andris Jaunzemis

"""

from golf_tee_set import GolfTeeSet

class GolfTrack(object):
    r"""
    Container for a track on a golf course.

    """

    def __init__(self, id: int, course_id: int, name: str, abbreviation: str):
        self.id = id
        self.course_id = course_id
        self.name = name
        self.abbreviation = abbreviation
        self.tee_sets = []

    def __str__(self):
        r"""
        Customizes string representation for this track.

        Returns
        -------
        s : string
            string representation of track

        """
        return "{:s}".format(self.name)
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this track.

        Returns
        -------
        track_dict : dict
            dictionary representation of track data

        """
        track_dict = {
            'id': self.id,
            'courseId': self.course_id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'teeSets': [tee_set.as_dict() for tee_set in self.tee_sets]
        }
        return track_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this track into database.

        Returns
        -------
        query : string
            database insert query for track

        """
        # Add required fields
        fields = "course_id, name, abbreviation"
        values = "{:d}, '{:s}', '{:s}'".format(self.course_id, self.name, self.abbreviation)

        # Construct query
        return "INSERT INTO tracks ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this track in database.

        Returns
        -------
        query : string
            database update query for track

        """
        # Add required fields
        fieldValues = "course_id = {:d}, name = '{:s}', abbreviation = '{:s}'".format(self.course_id, self.name, self.abbreviation)

        # Construct conditions
        if self.id is not None:
            conditions = "id = {:d}".format(self.id)
        else:
            conditions = "course_id = {:d} AND name = '{:s}'".format(self.course_id, self.name)

        # Construct query
        return "UPDATE tracks SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_tee_set(self, tee_set: GolfTeeSet):
        r"""
        Add a tee set to this track.

        Parameters
        ----------
        tee_set : GolfTeeSet
            tee set to add

        Raises
        ------
        ValueError :
            if track identifier for given tee set does not match this track identifier
            if this track already contains a tee set with the given name and gender
        
        """
        if tee_set.track_id != self.id:
            raise ValueError("Cannot add tee set with track id={:d} to track with id={:d}".format(tee_set.track_id, self.id))
        if tee_set.name in [t.name for t in self.tee_sets] and tee_set.gender in [t.gender for t in self.tee_sets]:
            raise ValueError("Track (id={:d}) already contains a tee set with name={:s}".format(self.id, tee_set.name))
        self.tee_sets.append(tee_set)
