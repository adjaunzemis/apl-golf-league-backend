r"""
Golf tee set data model

Authors
-------
Andris Jaunzemis

"""

from golf_hole import GolfHole

class GolfTeeSet(object):
    r"""
    Container class for a tee set on a golf course track.

    """

    def __init__(self, name: str, gender: str, rating: float, slope: float, color: str = None, tee_set_id: int = None, track_id: int = None):
        r"""
        """
        self.name = name
        self.gender = gender
        self.rating = rating
        self.slope = slope
        self.color = color
        self.tee_set_id = tee_set_id
        self.track_id = track_id
        self.holes = []

    def __str__(self):
        r"""
        Customizes string representation for this tee set.

        Returns
        -------
        s : string
            string representation of tee set

        """
        return "{:s} ({:s}: {:.1f}/{:.1f})".format(self.name, self.gender, self.rating, self.slope)
    
    @classmethod
    def from_dict(cls, tee_set_data):
        r"""
        Initializes tee set from dictionary representation.

        Parameters
        ----------
        tee_set_data : dict
            dictionary of tee set data

        Returns
        -------
        tee_set : GolfTeeSet
            tee set parsed from given data

        """
        tee_set = cls(
            tee_set_id = tee_set_data['tee_set_id'] if tee_set_data['tee_set_id'] != -1 else None,
            track_id = tee_set_data['track_id'] if tee_set_data['track_id'] != -1 else None,
            name = tee_set_data['name'],
            gender = tee_set_data['gender'],
            rating = tee_set_data['rating'],
            slope = tee_set_data['slope']
        )

        for key in ['color']:
            if key in tee_set_data:
                setattr(tee_set, key, tee_set_data[key])

        for hole_data in tee_set_data['holes']:
            tee_set.add_hole(GolfHole.from_dict(hole_data))

        return tee_set
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this tee set.

        Returns
        -------
        tee_set_dict : dict
            dictionary representation of tee set data

        """
        tee_set_dict = {
            'tee_set_id': self.tee_set_id,
            'track_id': self.track_id,
            'name': self.name,
            'gender': self.gender,
            'rating': self.rating,
            'slope': self.slope,
            'holes': [hole.as_dict() for hole in self.holes]
        }

        if self.color is not None:
            tee_set_dict['color'] = self.color

        return tee_set_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this tee set into database.

        Returns
        -------
        query : string
            database insert query for tee set

        """
        # Add required fields
        fields = "track_id, name, gender, rating, slope"
        values = "{:d}, '{:s}', '{:s}', {:f}, {:f}".format(self.track_id, self.name, self.gender, self.rating, self.slope)
        
        # Add optional fields if defined
        if self.color is not None:
            fields += ", color"
            values += ", '{:s}'".format(self.color)

        # Construct query
        return "INSERT INTO tee_sets ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this tee set in database.

        Returns
        -------
        query : string
            database update query for tee set

        """
        # Add required fields
        fieldValues = "track_id = {:d}, name = '{:s}', gender = '{:s}', rating = {:f}, slope = {:f}".format(self.track_id, self.name, self.gender, self.rating, self.slope)

        # Add optional fields if defined
        if self.color is not None:
            fieldValues += ", color = '{:s}'".format(self.color)
            
        # Construct conditions
        if self.tee_set_id is not None:
            conditions = "tee_set_id = {:d}".format(self.tee_set_id)
        else:
            conditions = "track_id = {:d} AND name = '{:s}' AND gender = '{:s}'".format(self.track_id, self.name, self.gender)

        # Construct query
        return "UPDATE tee_sets SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_hole(self, hole: GolfHole):
        r"""
        Add a hole to this tee set.

        Parameters
        ----------
        hole : GolfHole
            hole to add

        Raises
        ------
        ValueError :
            if tee set identifier for given hole does not match this tee set identifier
            if this tee set already contains a hole with the given number
        
        """
        if not isinstance(hole, GolfHole):
            raise ValueError("")
        if hole.tee_set_id != self.tee_set_id:
            raise ValueError("Cannot add hole with tee set id={:d} to tee set with id={:d}".format(hole.tee_set_id, self.tee_set_id))
        if hole.number in [h.number for h in self.holes]:
            raise ValueError("Tee set '{:s}' (id={:d}) already contains a hole with number={:d}".format(self.name, self.tee_set_id, hole.number))
        self.holes.append(hole)
