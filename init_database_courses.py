r"""
Script to initialize courses and course_holes tables in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_course import GolfCourse
from golf_track import GolfTrack
from golf_tee_set import GolfTeeSet
from golf_hole import GolfHole
from apl_golf_league_database import APLGolfLeagueDatabase


def init_db():
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    return APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)
    
def test_woodholme():
    # Create Woodholme course
    course = GolfCourse(
        None, # id (assigned by database)
        "Woodholme Country Club", # name
        "WCC" # abbreviation
    )
    course.address = "300 Woodholme Ave"
    course.city = "Pikesville"
    course.state = "MD"
    course.zip_code = 21208
    course.phone = "410-486-3700"
    course.website = "www.woodholme.org"

    # Add front track
    track_front = GolfTrack(
        None, # id (assigned by database)
        None, # course_id (assigned by database)
        "Front", # name
        "F", # abbreviation
    )
    course.add_track(track_front)

    # Add blue (M, front) tee set
    tee_set_blue_m_front = GolfTeeSet(
        None, # id (assigned by database)
        None, # track_id (assigned by database)
        "Blue", # name
        "M", # gender
        34.8, # rating
        133, # slope
        color="0000ff" # color (optional)
    )
    track_front.add_tee_set(tee_set_blue_m_front)

    # Add holes to blue (M, front) tee set
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        1, # number
        4, # par
        17, # handicap
        yardage=325, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        2, # number
        5, # par
        7, # handicap
        yardage=529, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        3, # number
        3, # par
        11, # handicap
        yardage=164, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        4, # number
        4, # par
        1, # handicap
        yardage=401, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        5, # number
        3, # par
        13, # handicap
        yardage=186, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        6, # number
        4, # par
        5, # handicap
        yardage=404, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        7, # number
        4, # par
        9, # handicap
        yardage=337, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        8, # number
        4, # par
        15, # handicap
        yardage=306, # yardage (optional)
    ))
    tee_set_blue_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        9, # number
        4, # par
        3, # handicap
        yardage=366, # yardage (optional)
    ))

    # Add white (M, front) tee set
    tee_set_white_m_front = GolfTeeSet(
        None, # id (assigned by database)
        None, # track_id (assigned by database)
        "White", # name
        "M", # gender
        33.6, # rating
        131, # slope
        color="ffffff" # color (optional)
    )
    track_front.add_tee_set(tee_set_white_m_front)

    # Add holes to white (M, front) tee set
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        1, # number
        4, # par
        17, # handicap
        yardage=318, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        2, # number
        5, # par
        7, # handicap
        yardage=496, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        3, # number
        3, # par
        11, # handicap
        yardage=125, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        4, # number
        4, # par
        1, # handicap
        yardage=361, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        5, # number
        3, # par
        13, # handicap
        yardage=181, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        6, # number
        4, # par
        5, # handicap
        yardage=359, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        7, # number
        4, # par
        9, # handicap
        yardage=320, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        8, # number
        4, # par
        15, # handicap
        yardage=291, # yardage (optional)
    ))
    tee_set_white_m_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        9, # number
        4, # par
        3, # handicap
        yardage=334, # yardage (optional)
    ))

    # Add white (F, front) tee set
    tee_set_white_f_front = GolfTeeSet(
        None, # id (assigned by database)
        None, # track_id (assigned by database)
        "White", # name
        "F", # gender
        36.1, # rating
        133, # slope
        color="ffffff" # color (optional)
    )
    track_front.add_tee_set(tee_set_white_f_front)

    # Add holes to white (F, front) tee set
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        1, # number
        4, # par
        13, # handicap
        yardage=318, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        2, # number
        5, # par
        1, # handicap
        yardage=496, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        3, # number
        3, # par
        17, # handicap
        yardage=125, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        4, # number
        4, # par
        5, # handicap
        yardage=361, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        5, # number
        3, # par
        11, # handicap
        yardage=181, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        6, # number
        4, # par
        7, # handicap
        yardage=359, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        7, # number
        4, # par
        9, # handicap
        yardage=320, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        8, # number
        4, # par
        15, # handicap
        yardage=291, # yardage (optional)
    ))
    tee_set_white_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        9, # number
        4, # par
        3, # handicap
        yardage=334, # yardage (optional)
    ))

    # Add green (F, front) tee set
    tee_set_green_f_front = GolfTeeSet(
        None, # id (assigned by database)
        None, # track_id (assigned by database)
        "Green", # name
        "F", # gender
        34.9, # rating
        127, # slope
        color="00ff00" # color (optional)
    )
    track_front.add_tee_set(tee_set_green_f_front)

    # Add holes to green (F, front) tee set
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        1, # number
        4, # par
        13, # handicap
        yardage=302, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        2, # number
        5, # par
        1, # handicap
        yardage=469, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        3, # number
        3, # par
        17, # handicap
        yardage=130, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        4, # number
        4, # par
        5, # handicap
        yardage=338, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        5, # number
        3, # par
        11, # handicap
        yardage=178, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        6, # number
        4, # par
        7, # handicap
        yardage=308, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        7, # number
        4, # par
        9, # handicap
        yardage=265, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        8, # number
        4, # par
        15, # handicap
        yardage=253, # yardage (optional)
    ))
    tee_set_green_f_front.add_hole(GolfHole(
        None, # id (assigned by database)
        None, # tee_set_id (assigned by database)
        9, # number
        4, # par
        3, # handicap
        yardage=318, # yardage (optional)
    ))

    # Display course data
    print(course)
    print(course.as_dict())
    
    # Add/update course in database
    db = init_db()
    db.put_course(course, update=True, verbose=True)

def main():
    # TODO: Rework for new database schema
    print("NOT READY FOR NEW DATABASE SCHEMA YET!")
    return

    # Read course data spreadsheet
    COURSES_SPREADSHEET = "data/courses_2019.csv"
    df = pd.read_csv(COURSES_SPREADSHEET)

    # For each course entry:
    courseList = []
    for idx, row in df.iterrows():
        # Create golf course object
        course = GolfCourse(
            None, # id (assigned by database on insertion)
            row['course_name'], # course name
            row['track_name'], # track name
            row['abbreviation'], # abbreviation
            row['tee_name'], # tee name
            "M", # gender # TODO: Add women's ratings to spreadsheet
            row['rating'], # course rating
            row['slope'] # slope rating
        )

        # Add optional parameters
        if pd.notna(row['address']):
            course.address = row['address']
        if pd.notna(row['city']):
            course.city = row['city']
        if pd.notna(row['state']):
            course.state = row['state']
        if pd.notna(row['zip_code']):
            course.zip_code = int(row['zip_code'])
        if pd.notna(row['phone']):
            course.phone = row['phone']
        if pd.notna(row['website']):
            course.website = row['website']

        # Add golf holes:
        for holeNum in range(1, 10):
            par = int(row['par' + str(holeNum)])
            hcp = 0 # TODO: Make sure each hole has handicap
            if pd.notna(row['hcp' + str(holeNum)]):
                hcp = int(row['hcp' + str(holeNum)])
            yds = 0 # TODO: Make sure each hole has yardage
            if pd.notna(row['yd' + str(holeNum)]):
                yds = int(row['yd' + str(holeNum)])
            course.create_hole(holeNum, par, hcp, yds)

        # Add to course list:
        courseList.append(course)

    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

    # For each golf course:
    for idx, course in enumerate(courseList):
        print("Adding/updating database course: {:s} ({:d}/{:d})".format(str(course), idx + 1, len(courseList)))
        db.put_course(course, update=True, verbose=False)
        
    # Check course list in database
    course_names = db.get_all_course_names(verbose=False)
    print(course_names)

if __name__ == "__main__":
    # main()
    test_woodholme()
