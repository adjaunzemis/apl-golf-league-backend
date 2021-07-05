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
    # Create course: Woodholme Country Club
    course = GolfCourse(
        name = "Woodholme Country Club",
        address = "300 Woodholme Ave",
        city = "Pikesville",
        state = "MD",
        zip_code = 21208,
        phone = "410-486-3700",
        website = "www.woodholme.org"
    )

    # Add track: Front
    track_front = GolfTrack(name="Front")
    course.add_track(track_front)

    # Add tee set: Blue, M (Front)
    tee_set_blue_m_front = GolfTeeSet(
        name = "Blue",
        gender = "M",
        rating = 34.8,
        slope = 133,
        color = "0000ff"
    )
    track_front.add_tee_set(tee_set_blue_m_front)

    # Add holes to tee set: Blue, M (Front)
    tee_set_blue_m_front.add_hole(GolfHole(number=1, par=4, handicap=17, yardage=325))
    tee_set_blue_m_front.add_hole(GolfHole(number=2, par=5, handicap=7, yardage=529))
    tee_set_blue_m_front.add_hole(GolfHole(number=3, par=3, handicap=11, yardage=164))
    tee_set_blue_m_front.add_hole(GolfHole(number=4, par=4, handicap=1, yardage=401))
    tee_set_blue_m_front.add_hole(GolfHole(number=5, par=3, handicap=13, yardage=186))
    tee_set_blue_m_front.add_hole(GolfHole(number=6, par=4, handicap=5, yardage=404))
    tee_set_blue_m_front.add_hole(GolfHole(number=7, par=4, handicap=9, yardage=337))
    tee_set_blue_m_front.add_hole(GolfHole(number=8, par=4, handicap=15, yardage=306))
    tee_set_blue_m_front.add_hole(GolfHole(number=9, par=4, handicap=3, yardage=366))

    # Add tee set: White, M (Front)
    tee_set_white_m_front = GolfTeeSet(
        name = "White",
        gender = "M",
        rating = 33.6,
        slope = 131,
        color = "ffffff"
    )
    track_front.add_tee_set(tee_set_white_m_front)
    
    # Add holes to tee set: White, M (Front)
    tee_set_white_m_front.add_hole(GolfHole(number=1, par=4, handicap=17, yardage=318))
    tee_set_white_m_front.add_hole(GolfHole(number=2, par=5, handicap=7, yardage=496))
    tee_set_white_m_front.add_hole(GolfHole(number=3, par=3, handicap=11, yardage=125))
    tee_set_white_m_front.add_hole(GolfHole(number=4, par=4, handicap=1, yardage=361))
    tee_set_white_m_front.add_hole(GolfHole(number=5, par=3, handicap=13, yardage=181))
    tee_set_white_m_front.add_hole(GolfHole(number=6, par=4, handicap=5, yardage=359))
    tee_set_white_m_front.add_hole(GolfHole(number=7, par=4, handicap=9, yardage=320))
    tee_set_white_m_front.add_hole(GolfHole(number=8, par=4, handicap=15, yardage=291))
    tee_set_white_m_front.add_hole(GolfHole(number=9, par=4, handicap=3, yardage=334))

    # Add white (F, front) tee set
    tee_set_white_f_front = GolfTeeSet(
        name = "White",
        gender = "F",
        rating = 36.1,
        slope = 133,
        color = "ffffff"
    )
    track_front.add_tee_set(tee_set_white_f_front)
    
    # Add holes to tee set: White, F (Front)
    tee_set_white_f_front.add_hole(GolfHole(number=1, par=4, handicap=13, yardage=318))
    tee_set_white_f_front.add_hole(GolfHole(number=2, par=5, handicap=1, yardage=496))
    tee_set_white_f_front.add_hole(GolfHole(number=3, par=3, handicap=17, yardage=125))
    tee_set_white_f_front.add_hole(GolfHole(number=4, par=4, handicap=5, yardage=361))
    tee_set_white_f_front.add_hole(GolfHole(number=5, par=3, handicap=11, yardage=181))
    tee_set_white_f_front.add_hole(GolfHole(number=6, par=4, handicap=7, yardage=359))
    tee_set_white_f_front.add_hole(GolfHole(number=7, par=4, handicap=9, yardage=320))
    tee_set_white_f_front.add_hole(GolfHole(number=8, par=4, handicap=15, yardage=291))
    tee_set_white_f_front.add_hole(GolfHole(number=9, par=4, handicap=3, yardage=334))

    # Add green (F, front) tee set
    tee_set_green_f_front = GolfTeeSet(
        name = "Green",
        gender = "F",
        rating = 34.9,
        slope = 127,
        color = "00ff00"
    )
    track_front.add_tee_set(tee_set_green_f_front)

    # Add holes to tee set: White, F (Front)
    tee_set_green_f_front.add_hole(GolfHole(number=1, par=4, handicap=13, yardage=302))
    tee_set_green_f_front.add_hole(GolfHole(number=2, par=5, handicap=1, yardage=469))
    tee_set_green_f_front.add_hole(GolfHole(number=3, par=3, handicap=17, yardage=130))
    tee_set_green_f_front.add_hole(GolfHole(number=4, par=4, handicap=5, yardage=338))
    tee_set_green_f_front.add_hole(GolfHole(number=5, par=3, handicap=11, yardage=178))
    tee_set_green_f_front.add_hole(GolfHole(number=6, par=4, handicap=7, yardage=308))
    tee_set_green_f_front.add_hole(GolfHole(number=7, par=4, handicap=9, yardage=265))
    tee_set_green_f_front.add_hole(GolfHole(number=8, par=4, handicap=15, yardage=253))
    tee_set_green_f_front.add_hole(GolfHole(number=9, par=4, handicap=3, yardage=318))

    # Display course data
    print(course)
    print(course.as_dict())
    
    # Add/update course in database
    db = init_db()
    db.put_course(course, update=False, verbose=True)

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
