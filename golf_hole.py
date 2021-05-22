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

    def __init__(self, id: int, tee_set_id: int, number: int, par: int, handicap: int):
        self.id = id
        self.tee_set_id = tee_set_id
        self.number = number
        self.par = par
        self.handicap = handicap
        self.yardage: int = None
    
    def __str__(self):
        r"""
        Customizes string representation for this hole.

        Returns
        -------
        s : string
            string representation of hole

        """
        return "{:d} (Par={:d}, Handicap={:d}, Yardage={:d})".format(self.number, self.par, self.handicap)
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this hole.

        Returns
        -------
        hole_dict : dict
            dictionary representation of hole data

        """
        hole_dict = {
            'id': self.id,
            'teeSetId': self.tee_set_id,
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
            values += ", '{:s}'".format(self.yardage)

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
            fieldValues += ", yardage = '{:s}'".format(self.yardage)
            
        # Construct conditions
        if self.id is not None:
            conditions = "id = {:d}".format(self.id)
        else:
            conditions = "tee_set_id = {:d}, number = '{:s}'".format(self.tee_set_id, self.number)

        # Construct query
        return "UPDATE courses SET {:s} WHERE {:s};".format(fieldValues, conditions)
