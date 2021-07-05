r"""
Golf hole data model

Authors
-------
Andris Jaunzemis

"""

class GolfHole(object):
    r"""
    Container class for hole on a golf tee set.

    """

    def __init__(self, number: int, par: int, handicap: int, yardage: int = None, hole_id: int = None, tee_set_id: int = None):
        self.hole_id = hole_id
        self.tee_set_id = tee_set_id
        self.number = number
        self.par = par
        self.handicap = handicap
        self.yardage = yardage
    
    def __str__(self):
        r"""
        Customizes string representation for this hole.

        Returns
        -------
        s : string
            string representation of hole

        """
        if self.yardage is not None:
            return "{:d} (Par={:d}, Handicap={:d}, Yardage={:d})".format(self.number, self.par, self.handicap, self.yardage)
        return "{:d} (Par={:d}, Handicap={:d}, Yardage=n/a)".format(self.number, self.par, self.handicap)
    
    @classmethod
    def from_dict(cls, hole_data):
        r"""
        Initializes hole from dictionary representation.

        Parameters
        ----------
        hole_data : dict
            dictionary of hole data

        Returns
        -------
        hole : GolfHole
            hole parsed from given data

        """
        hole = cls(
            hole_data['hole_id'] if hole_data['id'] != -1 else None,
            hole_data['tee_set_id'] if hole_data['tee_set_id'] != -1 else None,
            hole_data['number'],
            hole_data['par'],
            hole_data['handicap'],
            hole_data['yardage']
        )
        return hole
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this hole.

        Returns
        -------
        hole_dict : dict
            dictionary representation of hole data

        """
        hole_dict = {
            'hole_id': self.hole_id,
            'tee_set_id': self.tee_set_id,
            'number': self.number,
            'par': self.par,
            'handicap': self.handicap
        }

        if self.yardage is not None:
            hole_dict['yardage'] = self.yardage

        return hole_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this hole into database.

        Returns
        -------
        query : string
            database insert query for hole

        """
        # Add required fields
        fields = "tee_set_id, number, par, handicap"
        values = "{:d}, {:d}, {:d}, {:d}".format(self.tee_set_id, self.number, self.par, self.handicap)
        
        # Add optional fields if defined
        if self.yardage is not None:
            fields += ", yardage"
            values += ", {:d}".format(self.yardage)

        # Construct query
        return "INSERT INTO holes ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this hole in database.

        Returns
        -------
        query : string
            database update query for hole

        """
        # Add required fields
        fieldValues = "tee_set_id = {:d}, number = {:d}, par = {:d}, handicap = {:d}".format(self.tee_set_id, self.number, self.par, self.handicap)

        # Add optional fields if defined
        if self.yardage is not None:
            fieldValues += ", yardage = {:d}".format(self.yardage)
            
        # Construct conditions
        if self.hole_id is not None:
            conditions = "hole_id = {:d}".format(self.hole_id)
        else:
            conditions = "tee_set_id = {:d} AND number = {:d}".format(self.tee_set_id, self.number)

        # Construct query
        return "UPDATE holes SET {:s} WHERE {:s};".format(fieldValues, conditions)
