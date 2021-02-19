r"""
Test script for golf data model classes

Authors
-------
Andris Jaunzemis

"""

from datetime import date

from golf_models import GolfCourse, GolfHole, GolfRound, GolfPlayer, GolfFlight

def test_golf_round():
    # Create course
    course = GolfCourse(
        1,
        "Woodholme Country Club",
        "Front",
        "WCCF",
        "Blue",
        "M",
        34.8,
        133
    )
    course.city = "Pikesville"
    course.state = "MD"
    course.date_updated = date.today()

    # Add holes
    course.create_hole(1, 4, 17, 325)
    course.create_hole(2, 5, 7, 529)
    course.create_hole(3, 3, 11, 167)
    course.create_hole(4, 4, 1, 401)
    course.create_hole(5, 3, 13, 186)
    course.create_hole(6, 4, 5, 404)
    course.create_hole(7, 4, 9, 337)
    course.create_hole(8, 4, 15, 306)
    course.create_hole(9, 4, 3, 366)
    
    print(str(course))
    print(course.as_dict())
    print(course._create_database_insert_query())
    print(course._create_database_update_query())

    # Create round
    golf_round = GolfRound(course, None, date.today(), 16.5)

    # Add hole results
    golf_round.add_hole_score(1, 5)
    golf_round.add_hole_score(2, 5)
    golf_round.add_hole_score(3, 5)
    golf_round.add_hole_score(4, 5)
    golf_round.add_hole_score(5, 5)
    golf_round.add_hole_score(6, 10)
    golf_round.add_hole_score(7, 5)
    golf_round.add_hole_score(8, 5)
    golf_round.add_hole_score(9, 5)

    print(golf_round.as_dict())

def test_golf_player():
    player = GolfPlayer('Andris', 'Jaunzemis', 'APL_EMPLOYEE', 'Andris.Jaunzemis@jhuapl.edu')
    player.phone = '443-845-2306'
    player.location = '200-E342'
    player.employee_id = '123456'

    print(str(player))
    print(player.as_dict())
    print(player._create_database_insert_query())
    print(player._create_database_update_query(0))

def test_golf_flight():
    flight = GolfFlight("Diamond Ridge", 2019, "DR", 0, 1, 2, 3)

    print(str(flight))
    print(flight.as_dict())
    print(flight._create_database_insert_query())
    print(flight._create_database_update_query(0))

if __name__ == '__main__':
    test_golf_round()
    test_golf_player()
    test_golf_flight()
