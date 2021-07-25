r"""
Golf league flight data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime

from golf_flight_division import GolfFlightDivision

class GolfFlight(object):
    r"""
    Container class for a golf league flight

    """

    def __init__(self, name: str, year: int, home_course_id: int, flight_id: int = None, date_updated: datetime = None):
        self.name = name
        self.year = year
        self.home_course_id = home_course_id
        self.flight_id = flight_id
        self.date_updated = date_updated
        self.divisions = []

    def __str__(self):
        r"""
        Customizes string representation for this flight.

        Returns
        -------
        s : string
            string representation of flight

        """
        return "{:s} ({:d})".format(self.name, self.year)

    @classmethod
    def from_dict(cls, flight_data):
        r"""
        Initializes flight from dictionary representation.
        
        Parameters
        ----------
        flight_data : dict
            dictionary representation of flight data

        Returns
        -------
        flight : GolfFlight
            flight partse from given data

        """
        flight = cls(
            flight_id = flight_data['flight_id'] if flight_data['flight_id'] != -1 else None,
            name = flight_data['name'],
            year = flight_data['year'],
            home_course_id = flight_data['home_course_id']
        )

        for division_data in flight_data['divisions']:
            flight.add_division(GolfFlightDivision.from_dict(division_data))

        return flight

    def as_dict(self):
        r"""
        Creates dictionary representation of this flight.

        Returns
        -------
        flight_dict : dict
            dictionary representation of flight data

        """
        flight_dict = {
            'flight_id': self.flight_id,
            'name': self.name,
            'year': self.year,
            'home_course_id': self.home_course_id,
            'divisions': [division.as_dict() for division in self.divisions]
        }

        if self.date_updated is not None:
            flight_dict['date_updated'] = self.date_updated

        return flight_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this flight into database.

        Returns
        -------
        query : string
            database insert query for flight

        """
        # Add required fields
        fields = "name, year, home_course_id"
        values = "'{:s}', {:d}, {:d}".format(self.name, self.year, self.home_course_id)

        # Construct query
        return "INSERT INTO flights ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this flight in database.

        Returns
        -------
        query : string
            database update query for flight

        """
        # Add required fields
        fieldValues = "name = '{:s}', year = {:d}, home_course_id = {:d}".format(self.name, self.year, self.home_course_id)

        # Construct conditions
        if self.flight_id is None:
            raise ValueError("Cannot update flight data in database without flight_id")
        conditions = "flight_id = {:d}".format(self.flight_id)

        # Construct query
        return "UPDATE flights SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_division(self, division: GolfFlightDivision):
        r"""
        Add division to this flight.

        Parameters
        ----------
        division : GolfFlightDivision
            division to add

        Raises
        ------
        ValueError :
            if flight identifier for given division does not match this flight identifier

        """
        if division.flight_id != self.flight_id:
            raise ValueError("Cannot add division with flight_id={:d} to flight with id={:d}".format(division.flight_id, self.flight_id))
        self.divisions.append(division)
