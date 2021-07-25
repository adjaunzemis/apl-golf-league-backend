r"""
Golf league flight division data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime

from golf_tee_set import GolfTeeSet

class GolfFlightDivision(object):
    r"""
    Container class for a division within a golf league flight
    
    """

    def __init__(self, name: str, gender: str, home_tee_set_id: int, division_id: int = None, flight_id: int = None, date_updated: datetime = None):
        self.name = name
        self.gender = gender
        self.home_tee_set_id = home_tee_set_id
        self.division_id = division_id
        self.flight_id = flight_id
        self.date_updated = date_updated

    def __str__(self):
        r"""
        Customizes string representation for this division.

        Returns
        -------
        s : string
            string representation of division

        """
        return "{:s}".format(self.name)

    @classmethod
    def from_dict(cls, division_data):
        r"""
        Initializes division from dictionary representation.

        Parameters
        ----------
        division_data : dict
            dictionary of division data

        Returns
        -------
        division : GolfFlightDivision
            division parsed from given data

        """
        return cls(
            division_id = division_data['division_id'] if division_data['division_id'] != -1 else None,
            flight_id = division_data['flight_id'] if division_data['flight_id'] != -1 else None,
            name = division_data['name'],
            gender = division_data['gender'],
            home_tee_set_id = division_data['home_tee_set_id']
        )

    def as_dict(self):
        r"""
        Creates dictionary representation of this division.
        
        Returns
        -------
        division_dict : dict
            dictionary representation of division information

        """
        division_dict = {
            'division_id': self.division_id,
            'flight_id': self.flight_id,
            'name': self.name,
            'gender': self.gender,
            'home_tee_set_id': self.home_tee_set_id
        }

        if self.date_updated is not None:
            division_dict['date_updated'] = self.date_updated.strftime('%Y-%m-%d')
        
        return division_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this division into database.

        Returns
        -------
        query : string
            database insert query for division

        """
        # Add required fields
        fields = "flight_id, name, gender, home_tee_set_id"
        values = "{:d}, '{:s}', '{:s}', {:d}".format(self.flight_id, self.name, self.gender, self.home_tee_set_id)

        # Construct query
        return "INSERT INTO flight_divisions ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this division in database.
        
        Returns
        -------
        query : string
            database update query for division
            
        """
        # Add required fields
        fieldValues = "flight_id = {:d}, name = '{:s}', gender = '{:s}', home_tee_set_id = {:d}".format(self.flight_id, self.name, self.gender, self.home_tee_set_id)

        # Construct conditions
        if self.division_id is None:
            raise ValueError("Cannot update division in database without division_id")
        conditions = "division_id = {:d}".format(self.division_id)

        # Construct query
        return "UPDATE flight_divisions SET {:s} WHERE {:s};".format(fieldValues, conditions)
