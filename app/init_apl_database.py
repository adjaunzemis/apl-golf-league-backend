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
import numpy as np
import pandas as pd
from typing import List
from datetime import date, datetime
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
from models.match import Match
from models.round import Round
from models.hole_result import HoleResult
from models.match_round_link import MatchRoundLink
from utilities.apl_legacy_handicap_system import APLLegacyHandicapSystem

def find_courses_played(scores_file: str):
    """
    Finds all courses played in matches in the given scores file.

    Returns
    -------
    course_abbreviations : list of strings
        unique list of abbreviations for courses played

    """
    print(f"Finding courses played in scores file: {scores_file}")

    # Read scores data spreadsheet
    df_scores = pd.read_csv(scores_file)

    # For each scores entry, compile course abbreviations:
    course_abbreviations = []
    for idx, row in df_scores.iterrows():
        course_abbreviations.append(row['course_abbreviation'])
    
    # Filter unique abbreviations
    return np.unique(course_abbreviations)

def add_courses(session: Session, courses_file: str, courses_played: List[str]):
    """
    Adds course-related data in database.
    
    Populates the following tables: course, track, tee, hole

    """
    print(f"Adding course data from file: {courses_file}")

    # Read course data spreadsheet
    df = pd.read_csv(courses_file)
    
    year = int(courses_file.split(".")[0][-4:])

    # For each course entry:
    for idx, row in df.iterrows():
        # Check if course had any rounds played
        if row["abbreviation"] in courses_played:
            # Add course to database (if not already added)
            course_db = session.exec(select(Course).where(Course.name == row["course_name"])).all()
            if not course_db:
                print(f"Adding course: {row['course_name']}")
                course_db = Course(
                    name=row["course_name"],
                    year=year,
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

        # Handle misnamed home courses in flight info
        course_name = row['course']
        if course_name == "Northwest Park Course":
            course_name = "Northwest Golf Course"
            print(f"Adjusted flight course name: {row['course']} -> {course_name}")
        
        # Find home course
        course_db = session.exec(select(Course).where(Course.name == course_name)).all()
        if not course_db:
            raise ValueError(f"Cannot match home course in database: {course_name}")
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

    # Read roster data spreadsheet
    df_roster = pd.read_csv(roster_file)

    # Skip playoffs roster
    if flight_abbreviation.lower() == "playoffs":
        print("Skipping playoffs roster")
        return

    # Only process golfer data for subs roster
    if flight_abbreviation.lower() == "subs":
        print("Only processing golfer data for subs roster")
        
        # For each roster entry:
        for idx, row in df_roster.iterrows():
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

        return

    # Read flights data spreadsheet
    df_flights = pd.read_csv(flights_file)

    # Find flight
    flight_name = df_flights.loc[df_flights['abbreviation'] == flight_abbreviation.lower()].iloc[0]['name']
    flight_db = session.exec(select(Flight).where(Flight.name == flight_name).where(Flight.year == year)).all()
    if not flight_db:
        raise ValueError(f"Unable to find flight '{flight_name}-{year}'")
    flight_db = flight_db[0]

    # For each roster entry:
    for idx, row in df_roster.iterrows():
        print(f"Processing player: {row['name']}")
        
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
            raise ValueError(f"Unable to find division '{row['division']}'")
        division_db = division_db[0]
        
        # Add player to database
        player_db = Player(
            team_id=team_db.id,
            golfer_id=golfer_db.id,
            division_id=division_db.id,
            role="CAPTAIN" if is_captain else "PLAYER"
        )
        session.add(player_db)
        session.commit()

def add_matches(session: Session, scores_file: str, flights_file: str, courses_file: str, subs_file: str):
    """
    Adds match-related data in database.
    
    Populates the following tables: match, round, holeresult, matchroundlink

    """
    print(f"Adding match data from file: {scores_file}")

    year = int(scores_file.split("_")[-2])
    flight_abbreviation = scores_file.split("_")[-1][0:-4].upper()

    if flight_abbreviation.lower() == "playoffs":
        print("Skipping playoffs score data")
        return

    # Initialize handicap system
    alhs = APLLegacyHandicapSystem()

    # Read flights data spreadsheet
    df_flights = pd.read_csv(flights_file)

    # Find flight
    flight_name = df_flights.loc[df_flights['abbreviation'] == flight_abbreviation.lower()].iloc[0]['name']
    flight_db = session.exec(select(Flight).where(Flight.name == flight_name).where(Flight.year == year)).all()
    if not flight_db:
        raise ValueError(f"Unable to find flight '{flight_name}-{year}'")
    flight_db = flight_db[0]

    # Read courses data spreadsheet
    df_courses = pd.read_csv(courses_file)

    # Read scores data spreadsheet
    df_scores = pd.read_csv(scores_file)

    # Read substitute roster data spreadsheet
    df_subs = pd.read_csv(subs_file)

    # For each scores entry:
    for idx, row in df_scores.iterrows():
        print(f"Adding match: {flight_abbreviation}-{year} week {row['week']} {row['team_1']}v{row['team_2']}")

        # Find match course
        course_name = df_courses.loc[df_courses['abbreviation'] == row['course_abbreviation']].iloc[0]['course_name']
        course_db = session.exec(select(Course).where(Course.name == course_name)).all()
        if not course_db:
            raise ValueError(f"Unable to find course '{course_name}' ({row['course_abbreviation']})")
        course_db = course_db[0]

        # Find match teams
        home_team_db = session.exec(select(Team).where(Team.flight_id == flight_db.id).where(Team.name == f"{flight_abbreviation.upper()}-{row['team_1']}")).all()
        if not home_team_db:
            raise ValueError(f"Unable to find home team")
        home_team_db = home_team_db[0]

        away_team_db = session.exec(select(Team).where(Team.flight_id == flight_db.id).where(Team.name == f"{flight_abbreviation.upper()}-{row['team_2']}")).all()
        if not away_team_db:
            raise ValueError(f"Unable to find away team")
        away_team_db = away_team_db[0]

        # Add match
        match_db = session.exec(select(Match).where(Match.flight_id == flight_db.id).where(Match.week == row['week']).where(Match.home_team_id == home_team_db.id).where(Match.away_team_id == away_team_db.id)).all()
        if not match_db:
            match_db = Match(
                flight_id=flight_db.id,
                week=row['week'],
                home_team_id=home_team_db.id,
                away_team_id=away_team_db.id,
                home_score=row['team_1_score'],
                away_score=row['team_2_score']
            )
            session.add(match_db)
            session.commit()
        else:
            print(f"Match already exists")
            match_db = match_db[0]

        # For each round:
        for pNum in [1, 2, 3, 4]:
            if pNum < 3:
                team_db = home_team_db
            else:
                team_db = away_team_db
                
            # Find golfer
            golfer_name = row[f"p{pNum}_name"]
            if golfer_name[-6:] == " (sub)":
                golfer_name = golfer_name[:-6]
            golfer_db = session.exec(select(Golfer).where(Golfer.name == golfer_name)).all()
            if not golfer_db:
                raise ValueError(f"Unable to find golfer '{golfer_name}'")
            golfer_db = golfer_db[0]

            # Find player
            player_db = session.exec(select(Player).where(Player.team_id == team_db.id).where(Player.golfer_id == golfer_db.id)).all()
            if not player_db:
                division_db: Division = None

                # Find other player entries for golfer
                players_db = session.exec(select(Player).where(Player.golfer_id == golfer_db.id)).all()
                if not players_db:
                    player_division_name = df_subs.loc[df_subs['name'] == golfer_name].iloc[0]['division']
                    division_db = session.exec(select(Division).where(Division.flight_id == team_db.flight_id).where(Division.name == player_division_name)).one()
                else:
                    # Determine appropriate division in this flight based on other player entries
                    for player_db in players_db:
                        player_division_db = session.exec(select(Division).where(Division.id == player_db.division_id)).one()
                        player_flight_db = session.exec(select(Flight).where(Flight.id == player_division_db.flight_id)).one()
                        if player_flight_db.year == year:
                            division_db = session.exec(select(Division).where(Division.flight_id == team_db.flight_id).where(Division.name == player_division_db.name)).one()
                if not division_db:
                    raise ValueError(f"Unable to find suitable division for golfer '{golfer_db.name}' in flight '{flight_db.name}-{year}'")
                    
                # Add player as substitute
                print(f"Adding substitute '{golfer_db.name}' to team '{team_db.name}' in division '{division_db.name}'")
                player_db = Player(
                    team_id=team_db.id,
                    golfer_id=golfer_db.id,
                    division_id=division_db.id,
                    role="SUBSTITUTE"
                )
                session.add(player_db)
                session.commit()
            else:
                player_db = player_db[0]

            # Find division
            division_db = session.exec(select(Division).where(Division.id == player_db.division_id)).one()

            # Find division home tee
            home_tee_db = session.exec(select(Tee).where(Tee.id == division_db.home_tee_id)).one()

            # Find division home track
            home_track_db = session.exec(select(Track).where(Track.id == home_tee_db.track_id)).one()

            # Find round tee
            if (flight_db.home_course_id == course_db.id) and (home_track_db.name[0].upper() == row['course_abbreviation'][-1].upper()):
                tee_db = home_tee_db # round played at home course
            else:
                print(f"Match played at non-home course: {row['course_abbreviation']}")

                # Find round track
                tracks_db = session.exec(select(Track).where(Track.course_id == course_db.id)).all()
                if not tracks_db:
                    raise ValueError(f"Unable to find tracks for course '{course_db.name}'")

                # Find track based on match course abbreviation
                track_db = None
                for tIdx in range(len(tracks_db)):
                    if tracks_db[tIdx].name[0] == row['course_abbreviation'][-1]:
                        track_db = tracks_db[tIdx]
                if not track_db:
                    raise ValueError(f"Unable to find track for course '{course_db.name}' matching abbreviation '{row['course_abbreviation']}'")

                # Find round tee
                tee_db = session.exec(select(Tee).where(Tee.track_id == track_db.id).where(Tee.name == home_tee_db.name)).one()

            # Parse round date played
            date_played = datetime.strptime(row[f'p{pNum}_date_played'], '%Y-%m-%d').date()

            # Add round
            round_db = session.exec(select(Round).where(Round.golfer_id == golfer_db.id).where(Round.date_played == date_played)).all()
            if not round_db:
                print(f"Adding round: {golfer_db.name} at {course_db.name} on {date_played}")
                round_db = Round(
                    tee_id=tee_db.id,
                    golfer_id=golfer_db.id,
                    date_played=date_played,
                    handicap_index=row[f"p{pNum}_handicap"],
                    playing_handicap=alhs.compute_course_handicap( # TODO: Use "adjusted handicap" calculation for playing handicap
                        par=tee_db.par,
                        rating=tee_db.rating,
                        slope=tee_db.slope,
                        handicap_index=row[f"p{pNum}_handicap"]
                    )
                )
                session.add(round_db)
                session.commit()
            else:
                round_db = round_db[0]

            # Add match-round-link
            link_db = session.exec(select(MatchRoundLink).where(MatchRoundLink.match_id == match_db.id).where(MatchRoundLink.round_id == round_db.id)).all()
            if not link_db:
                print(f"Adding match-round link: match_id = {match_db.id}, round_id = {round_db.id}")
                link_db = MatchRoundLink(
                    match_id=match_db.id,
                    round_id=round_db.id
                )
                session.add(link_db)
                session.commit()

            # Add round hole results
            hole_results_db = session.exec(select(HoleResult).where(HoleResult.round_id == round_db.id)).all()

            for hole_db in tee_db.holes:
                if hole_db.id not in [h.hole_id for h in hole_results_db]:
                    print(f"Adding hole #{hole_db.number} result")
                    hNum = hole_db.number
                    if hNum > 9:
                        hNum -= 9
                    gross_score = row[f"p{pNum}_h{hNum}_score"]
                    handicap_strokes = alhs.compute_hole_handicap_strokes(hole_db.stroke_index, round_db.playing_handicap)
                    hole_result_db = HoleResult(
                        round_id=round_db.id,
                        hole_id=hole_db.id,
                        handicap_strokes=handicap_strokes,
                        gross_score=gross_score,
                        adjusted_gross_score=alhs.compute_hole_adjusted_gross_score(hole_db.par, hole_db.stroke_index, gross_score, course_handicap=round_db.playing_handicap),
                        net_score=(gross_score - handicap_strokes)
                    )
                    session.add(hole_result_db)
                    session.commit()

if __name__ == "__main__":
    DELETE_EXISTING_DATABASE = True
    DATA_DIR = "data/"
    DATA_YEAR = 2021

    DATABASE_FILE = "apl.db"

    if DELETE_EXISTING_DATABASE and os.path.isfile(DATABASE_FILE):
        print(f"Deleting existing database: {DATABASE_FILE}")
        os.remove(DATABASE_FILE)
    
    print(f"Initializing database: {DATABASE_FILE}")
    engine = create_engine(
        f"sqlite:///{DATABASE_FILE}",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)  

    with Session(engine) as session:
        # Find all courses played in rounds for this year
        scores_files = [f"{DATA_DIR}/{f}" for f in os.listdir(DATA_DIR) if f[0:12] == f"scores_{DATA_YEAR}_"]
        courses_played = []
        for scores_file in scores_files:
            for course_played in find_courses_played(scores_file):
                if course_played not in courses_played:
                    courses_played.append(course_played)
        print(f"Courses played: {courses_played}")

        # Add relevant course data to database
        courses_file = f"{DATA_DIR}/courses_{DATA_YEAR}.csv"
        add_courses(session, courses_file, courses_played)

        # Add flight data to database
        flights_file = f"{DATA_DIR}/flights_{DATA_YEAR}.csv"
        add_flights(session, flights_file)

        # Add roster data into database
        roster_files = [f"{DATA_DIR}/{f}" for f in os.listdir(DATA_DIR) if f[0:12] == f"roster_{DATA_YEAR}_"]
        for roster_file in roster_files:
            add_teams(session, roster_file, flights_file)

        # Add score data to database
        for scores_file in scores_files:
            add_matches(session, scores_file, flights_file, courses_file, f"{DATA_DIR}/roster_{DATA_YEAR}_subs.csv")

    print("Database initialized!")
