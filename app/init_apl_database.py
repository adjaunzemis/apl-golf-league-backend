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
from models.golfer import Golfer
from models.team import Team
from models.player import Player

def add_courses(session: Session, courses_file: str):
    """
    Adds course-related data in database.
    
    Populates the following tables: course, track, tee, hole

    """
    print(f"Adding course data from file: {courses_file}")

    # Read course data spreadsheet
    df = pd.read_csv(courses_file)
    
    year = int(courses_file.split(".")[0][-4:]) # TODO: Add year to course info

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
            print(f"Adding track: {row['track_name']}")
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

def add_flights(session: Session, flights_file: str):
    """
    Adds flight-related data in database.
    
    Populates the following tables: flight, division

    """
    print(f"Adding flight data from file: {flights_file}")

    year = int(flights_file.split(".")[0][-4:])

    # Read flight data spreadsheet
    df_flights = pd.read_csv(flights_file)

    # For each flight:
    for idx, row in df_flights.iterrows():
        if row['abbreviation'].lower() == "playoffs":
            print(f"Skipping flight: {row['name']}")
            continue

        print(f"Adding flight: {row['name']}")

        # Find home course
        course_db = session.exec(select(Course).where(Course.name == row["course"])).all()
        if not course_db:
            raise ValueError(f"Cannot match home course in database: {row['course']}")
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
                raise ValueError(f"Cannot match home flight in database: Front")
            else:
                track_db = track_db[0]

                # For each division in this flight:
                for div_num in [1, 2, 3]:
                    division_name = row[f"division_{div_num}_name"].capitalize()
                    print(f"Adding division: {division_name}")

                    # Find home tees
                    tee_gender = "F" if division_name.lower() == "forward" else "M"
                    tee_db = session.exec(select(Tee).where(Tee.track_id == track_db.id).where(Tee.name == division_name).where(Tee.gender == tee_gender)).all()
                    if not tee_db:
                        raise ValueError(f"Cannot match home tee in database: {row[f'division_{div_num}_tee']}")
                    else:
                        tee_db = tee_db[0]

                        # Add division to database
                        division_db = Division(
                            flight_id=flight_db.id,
                            name=division_name,
                            gender=tee_gender,
                            home_tee_id=tee_db.id
                        )
                        session.add(division_db)
                        session.commit()

                    # Add super senior division (same tees as forward division with 'M' gender)
                    if division_name.lower() == "forward":
                        print(f"Adding division: SuperSenior")
                        tee_db = session.exec(select(Tee).where(Tee.track_id == track_db.id).where(Tee.name == "Super-Senior").where(Tee.gender == "M")).all()
                        if not tee_db:
                            raise ValueError(f"Cannot match home tee in database: Super-Senior")
                        else:
                            tee_db = tee_db[0]

                            # Add division to database
                            division_db = Division(
                                flight_id=flight_db.id,
                                name="SuperSenior",
                                gender="M",
                                home_tee_id=tee_db.id
                            )
                            session.add(division_db)
                            session.commit()

def add_teams(session: Session, roster_file: str, flights_file: str):
    """
    Adds team-related data in database.
    
    Populates the following tables: team, golfer, player

    """
    print(f"Adding team data from file: {roster_file}")

    year = int(roster_file.split("_")[-2])
    flight_abbreviation = roster_file.split("_")[-1][0:-4].upper()

    if flight_abbreviation.lower() == "playoffs":
        print("Skipping playoffs roster data")
        return

    # Read flights data spreadsheet
    df_flights = pd.read_csv(flights_file)

    # Find flight
    flight_name = df_flights.loc[df_flights['abbreviation'] == flight_abbreviation.lower()].iloc[0]['name']
    flight_db = session.exec(select(Flight).where(Flight.name == flight_name).where(Flight.year == year)).all()
    if not flight_db:
        raise ValueError(f"Unable to find flight '{flight_name}-{year}' in database")
    flight_db = flight_db[0]

    # Read roster data spreadsheet
    df_roster = pd.read_csv(roster_file)

    # For each roster entry:
    for idx, row in df_roster.iterrows():
        print(f"Adding player: {row['name']}")
        
        # Find golfer
        golfer_db = session.exec(select(Golfer).where(Golfer.name == row["name"])).all()
        if not golfer_db:
            print(f"Adding golfer: {row['name']}")

            # Add golfer to database
            # TODO: Add contact info
            affiliation = "APL_RETIREE" if row['affiliation'].lower() == "retiree" else "APL_FAMILY" if row['affiliation'].lower() == "apl_family_member" else row['affiliation'].upper()
            golfer_db = Golfer(
                name=row['name'],
                affiliation=affiliation
            )
            session.add(golfer_db)
            session.commit()
        else:
            golfer_db = golfer_db[0]

        # Find team
        is_captain = False
        team_name = f"{flight_abbreviation}-{row['team']}"
        team_db = session.exec(select(Team).where(Team.name == team_name)).all()
        if not team_db:
            print(f"Adding team: {team_name}")
            is_captain = True
            
            # Add team to database
            team_db = Team(
                name=team_name,
                flight_id=flight_db.id
            )
            
            session.add(team_db)
            session.commit()
        else:
            team_db = team_db[0]

        # Find division
        division_db = session.exec(select(Division).where(Division.flight_id == team_db.flight_id).where(Division.name == row['division'])).all()
        if not division_db:
            raise ValueError(f"Unable to find division '{row['division']}' in database")
        division_db = division_db[0]
        
        # Add player to database
        player_db = Player(
            team_id = team_db.id,
            golfer_id=golfer_db.id,
            division_id=division_db.id,
            role="CAPTAIN" if is_captain else "PLAYER"
        )
        session.add(player_db)
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
        add_flights(session, flights_file)

        roster_files = [f"{DATA_DIR}/{f}" for f in os.listdir(DATA_DIR) if f[0:12] == f"roster_{DATA_YEAR}_"]
        for roster_file in roster_files:
            add_teams(session, roster_file, flights_file)

    print("Database initialized!")
