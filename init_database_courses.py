r"""
Script to initialize courses table in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_models import GolfCourse
from apl_golf_league_database import APLGolfLeagueDatabase

def main():
    # Read course data spreadsheet
    COURSES_SPREADSHEET = "apl_courses_2019.csv"
    df = pd.read_csv(COURSES_SPREADSHEET)

    # For each course entry:
    courseList = []
    for idx, row in df.iterrows():
        # Create golf course object
        course = GolfCourse(
            row['name'], # course name
            row['track'], # track name
            row['shortname'], # abbreviation
            row['teeSet'], # tee set
            "M", # gender # TODO: Add this to spreadsheet
            row['rating'], # course rating
            row['slope'] # slope rating
        )

        # Add golf holes:
        for holeNum in range(1, 10):
            par = int(row['par' + str(holeNum)])
            if pd.notna(row['hcp' + str(holeNum)]):
                hcp = int(row['hcp' + str(holeNum)])
            else:
                hcp = 0 # TODO: Make sure each hole has handicap set
            yds = 123 # TODO: Add yardage to spreadsheet
            course.add_hole(holeNum, par, hcp, yds)

        # Add to course list:
        courseList.append(course)

    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=True)

    # For each golf course:
    for course in courseList:
        db.add_course(course, verbose=True)
        
    # Check course list in database
    course_names = db.fetch_all_course_names(verbose=True)
    print(course_names)
        
if __name__ == "__main__":
    main()
