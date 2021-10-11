r"""
Script to initialize course data in database

Populates the following tables:
- course
- track
- tee
- hole

Authors
-------
Andris Jaunzemis

"""

import os
import pandas as pd
from datetime import date
from sqlmodel import Session, SQLModel, create_engine, select

from models.course import Course
from models.track import Track
from models.tee import Tee
from models.hole import Hole

def add_courses(session: Session, courses_file: str):
    """
    Adds course-related data in database.
    
    Populates the following tables: course, track, tee, hole

    """
    print(f"Adding course data from file: {courses_file}")

    # Read course data spreadsheet
    df = pd.read_csv(courses_file)

    # For each course entry:
    for idx, row in df.iterrows():
        # Add course to database (if not already added)
        course_db = session.exec(select(Course).where(Course.name == row["course_name"])).all()
        if not course_db:
            print(f"\tAdding new course: {row['course_name']}")
            course_db = Course(
                name=row["course_name"],
                location=row["address"] if pd.notna(row["address"]) else None,
                phone=row["phone"] if pd.notna(row["phone"]) else None,
                website=row["website"] if pd.notna(row["website"]) else None
            )
            session.add(course_db)
            session.commit()
        else:
            course_db = course_db[0]

        # Add track to database
        track_db = Track(
            course_id=course_db.id,
            name=row["track_name"]
        )
        session.add(track_db)
        session.commit()

        # Add tee to database
        tee_db = Tee(
            track_id=track_db.id,
            name=row["tee_name"],
            gender="F" if row["tee_name"].lower() == "forward" else "M",
            rating=float(row["rating"]),
            slope=int(row["slope"]),
            color=row["tee_color"] if pd.notna(row["tee_color"]) else None
        )
        session.add(tee_db)
        session.commit()

        # Add holes to database
        holeOffset = 0 if row["track_name"].lower() != "back" else 9
        for holeNum in range(1, 10):
            par = int(row['par' + str(holeNum)])

            hcp = 0 # TODO: make optional?
            if pd.notna(row['hcp' + str(holeNum)]):
                hcp = int(row['hcp' + str(holeNum)])

            yds = 0 # TODO: make optional?
            if pd.notna(row['yd' + str(holeNum)]):
                yds = int(row['yd' + str(holeNum)])

            hole_db = Hole(
                tee_id=tee_db.id,
                number=holeNum + holeOffset,
                par=par,
                yardage=yds,
                stroke_index=hcp
            )
            session.add(hole_db)
        session.commit()

if __name__ == "__main__":
    DATA_DIR = "data/"
    DATA_YEAR = 2021

    DATABASE_FILE = "apl.db"

    if os.path.isfile(DATABASE_FILE):
        print(f"Removing existing database: {DATABASE_FILE}")
        os.remove(DATABASE_FILE)
    
    print(f"Initializing database: {DATABASE_FILE}")
    engine = create_engine(
        f"sqlite:///{DATABASE_FILE}",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)  

    with Session(engine) as session:
        add_courses(session, f"{DATA_DIR}/courses_{DATA_YEAR}.csv")

    print("Database initialized!")
