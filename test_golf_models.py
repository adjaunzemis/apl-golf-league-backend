r"""
Test script for golf data model classes

Authors
-------
Andris Jaunzemis

"""

from datetime import date

from golf_models import GolfCourse, GolfRound

def main():
    # Create course
    course = GolfCourse(
        "Woodholme Country Club",
        "Front",
        "WCCF",
        "Blue",
        "M",
        34.8,
        133
    )

    # Add holes
    course.add_hole(1, 4, 325, 17)
    course.add_hole(2, 5, 529, 7)
    course.add_hole(3, 3, 167, 11)
    course.add_hole(4, 4, 401, 1)
    course.add_hole(5, 3, 186, 13)
    course.add_hole(6, 4, 404, 5)
    course.add_hole(7, 4, 337, 9)
    course.add_hole(8, 4, 306, 15)
    course.add_hole(9, 4, 366, 3)
    
    print(course.as_dict())
    print(course._create_database_insert_query())

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

if __name__ == '__main__':
    main()
