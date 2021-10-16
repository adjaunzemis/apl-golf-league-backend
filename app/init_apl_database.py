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
from models.flight import Flight
from models.division import Division

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
            print(f"Adding course: {row['course_name']}")
            course_db = Course(
                name=row["course_name"],
                address=row["address"] if pd.notna(row["address"]) else None,
                phone=row["phone"] if pd.notna(row["phone"]) else None,
                website=row["website"] if pd.notna(row["website"]) else None
            )
            session.add(course_db)
            session.commit()
        else:
            course_db = course_db[0]

        # Add track to database (if not already added)
        track_db = session.exec(select(Track).where(Track.course_id == course_db.id).where(Track.name == row["track_name"])).all()
        if not track_db:
            print(f"\tAdding track: {row['track_name']}")
            track_db = Track(
                course_id=course_db.id,
                name=row["track_name"]
            )
            session.add(track_db)
            session.commit()
        else:
            track_db = track_db[0]

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

            hcp = None
            if pd.notna(row['hcp' + str(holeNum)]):
                hcp = int(row['hcp' + str(holeNum)])

            yds = None
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

def add_flights(session: Session, flights_file: str, courses_file: str):
    """
    Adds flight-related data in database.
    
    Populates the following tables: flight, division

    """
    print(f"Adding flight data from file: {flights_file}")

    year = flights_file.split(".")[0][-4:]

    # Read flight data spreadsheet
    df_flights = pd.read_csv(flights_file)

    # For each flight:
    for idx, row in df_flights.iterrows():
        print(f"Adding flight: {row['name']}")

        # Find home course
        course_db = session.exec(select(Course).where(Course.name == row["course"])).all()
        if not course_db:
            print(f"\tERROR: Cannot match home course in database: {row['course']}")
        else:
            course_db = course_db[0]

            # Add flight to database
            # TODO: Add secretary and other details
            flight_db = Flight(
                name=row["name"],
                year=year,
                home_course_id=course_db.id
            )
            session.add(flight_db)
            session.commit()

            # Find home track
            track_db = session.exec(select(Track).where(Track.course_id == course_db.id).where(Track.name == "Front")).all()
            if not track_db:
                print(f"\tERROR: Cannot match home flight in database: Front")
            else:
                track_db = track_db[0]

                # For each division in this flight:
                for div_num in [1, 2, 3]:
                    division_name = row[f"division_{div_num}_name"].capitalize()
                    print(f"\tAdding division: {division_name}")

                    # Find home tees
                    tee_db = session.exec(select(Tee).where(Tee.track_id == track_db.id).where(Tee.name == row[f"division_{div_num}_name"].capitalize())).all()
                    if not tee_db:
                        print(f"\tERROR: Cannot match home tee in database: {row[f'division_{div_num}_tee']}")
                    else:
                        tee_db = tee_db[0]

                        # Add division to database
                        division_db = Division(
                            flight_id=flight_db.id,
                            name=division_name,
                            gender="F" if division_name.lower() == "forward" else "M",
                            home_tee_id=tee_db.id
                        )
                        session.add(division_db)
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
        courses_file = f"{DATA_DIR}/courses_{DATA_YEAR}.csv"
        add_courses(session, courses_file)

        flights_file = f"{DATA_DIR}/flights_{DATA_YEAR}.csv"
        add_flights(session, flights_file, courses_file)

    print("Database initialized!")
