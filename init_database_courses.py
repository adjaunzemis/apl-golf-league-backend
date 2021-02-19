r"""
Script to initialize courses and course_holes tables in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_models import GolfCourse
from apl_golf_league_database import APLGolfLeagueDatabase

def main():
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
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=True)

    # For each golf course:
    for course in courseList:
        db.put_course(course, update=True, verbose=True)
        
    # Check course list in database
    course_names = db.get_all_course_names(verbose=True)
    print(course_names)
        
if __name__ == "__main__":
    main()
