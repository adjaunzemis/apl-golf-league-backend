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

    def __init__(self, name: str = None, track_id: int = None, course_id: int = None):
        self.name = name
        self.track_id = track_id
        self.course_id = course_id
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

    @classmethod
    def from_dict(cls, track_data):
        r"""
        Initializes track from dictionary representation.

        Parameters
        ----------
        track_data : dict
            dictionary of track data

        Returns
        -------
        track : GolfTrack
            track parsed from given data

        """
        track = cls(
            track_data['track_id'] if track_data['track_id'] != -1 else None,
            track_data['course_id'] if track_data['course_id'] != -1 else None,
            track_data['name']
        )

        for tee_set_data in track_data['tee_sets']:
            track.add_tee_set(GolfTeeSet.from_dict(tee_set_data))

        return track
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this track.

        Returns
        -------
        track_dict : dict
            dictionary representation of track data

        """
        track_dict = {
            'track_id': self.track_id,
            'course_id': self.course_id,
            'name': self.name,
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
        fields = "course_id, name"
        values = "{:d}, '{:s}'".format(self.course_id, self.name)

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
        fieldValues = "course_id = {:d}, name = '{:s}'".format(self.course_id, self.name)

        # Construct conditions
        if self.track_id is not None:
            conditions = "track_id = {:d}".format(self.track_id)
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
        if tee_set.track_id != self.track_id:
            raise ValueError("Cannot add tee set with track id={:d} to track with id={:d}".format(tee_set.track_id, self.track_id))
        for t in self.tee_sets:
            if (t.name == tee_set.name) and (t.gender == tee_set.gender):
                raise ValueError("Track '{:s}' (id={:d}) already contains a tee set with name='{:s}' and gender='{:s}'".format(self.name, self.track_id, tee_set.name, tee_set.gender))
        self.tee_sets.append(tee_set)
