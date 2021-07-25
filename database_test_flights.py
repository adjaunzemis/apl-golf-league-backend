r"""
Script to initialize flights and flight_divisions tables in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_flight import GolfFlight
from golf_flight_division import GolfFlightDivision
from apl_golf_league_database import APLGolfLeagueDatabase


def init_db():
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    return APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

def test_mock_flights():
    # Create list of mock flights
    flights = []

    dr = GolfFlight(
        name = "WCC",
        year = 2021,
        home_course_id = 1
    )
    dr.add_division(GolfFlightDivision(
        name = "Men Middle",
        gender = "M",
        home_tee_set_id = 1
    ))
    dr.add_division(GolfFlightDivision(
        name = "Men Senior",
        gender = "M",
        home_tee_set_id = 2
    ))
    dr.add_division(GolfFlightDivision(
        name = "Women Middle",
        gender = "F",
        home_tee_set_id = 4
    ))
    flights.append(dr)

    # Initialize database connection
    db = init_db()

    for flight in flights:
        # Display flight data
        print(flight)
        print(flight.as_dict())

        # Add/update flight in database
        db.put_flight(flight, update=True, verbose=True)

if __name__ == "__main__":
    test_mock_flights()
