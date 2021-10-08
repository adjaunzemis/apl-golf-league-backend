import os
from datetime import date
from sqlmodel import Session, SQLModel, create_engine

from models.course import Course
from models.track import Track
from models.tee import Tee
from models.hole import Hole
from models.golfer import Golfer
from models.flight import Flight
from models.division import Division
from models.team import Team
from models.player import Player
from models.match import Match
from models.round import Round
from models.hole_result import HoleResult
from models.match_round_link import MatchRoundLink

def add_course(session: Session, name: str):
    print(f"Adding course: {name}")

    course = Course(name=name, location="Test Location", phone="123-456-7890", website="google.com")
    session.add(course)
    session.commit()

    track_front = Track(name="Front", course_id=course.id)
    session.add(track_front)
    session.commit()

    tee_front_white_m = Tee(name="White", gender="M", rating=35.1, slope=126, color="white", track_id=track_front.id)
    session.add(tee_front_white_m)
    session.commit()

    session.add(Hole(number=1, par=4, yardage=383, stroke_index=7, tee_id=tee_front_white_m.id))
    session.add(Hole(number=2, par=4, yardage=383, stroke_index=5, tee_id=tee_front_white_m.id))
    session.add(Hole(number=3, par=4, yardage=429, stroke_index=1, tee_id=tee_front_white_m.id))
    session.add(Hole(number=4, par=4, yardage=359, stroke_index=11, tee_id=tee_front_white_m.id))
    session.add(Hole(number=5, par=3, yardage=197, stroke_index=3, tee_id=tee_front_white_m.id))
    session.add(Hole(number=6, par=4, yardage=345, stroke_index=9, tee_id=tee_front_white_m.id))
    session.add(Hole(number=7, par=4, yardage=314, stroke_index=13, tee_id=tee_front_white_m.id))
    session.add(Hole(number=8, par=3, yardage=146, stroke_index=17, tee_id=tee_front_white_m.id))
    session.add(Hole(number=9, par=5, yardage=492, stroke_index=15, tee_id=tee_front_white_m.id))
    session.commit()
    
    tee_front_gold_m = Tee(name="Gold", gender="M", rating=33.9, slope=115, color="gold", track_id=track_front.id)
    session.add(tee_front_gold_m)
    session.commit()

    session.add(Hole(number=1, par=4, yardage=372, stroke_index=7, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=2, par=4, yardage=363, stroke_index=5, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=3, par=4, yardage=415, stroke_index=1, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=4, par=4, yardage=346, stroke_index=11, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=5, par=3, yardage=175, stroke_index=3, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=6, par=4, yardage=330, stroke_index=9, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=7, par=4, yardage=287, stroke_index=13, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=8, par=3, yardage=100, stroke_index=17, tee_id=tee_front_gold_m.id))
    session.add(Hole(number=9, par=5, yardage=415, stroke_index=15, tee_id=tee_front_gold_m.id))
    session.commit()

    tee_front_red_f = Tee(name="Red", gender="F", rating=36.3, slope=128, color="red", track_id=track_front.id)
    session.add(tee_front_red_f)
    session.commit()

    session.add(Hole(number=1, par=4, yardage=353, stroke_index=3, tee_id=tee_front_red_f.id))
    session.add(Hole(number=2, par=4, yardage=348, stroke_index=7, tee_id=tee_front_red_f.id))
    session.add(Hole(number=3, par=5, yardage=401, stroke_index=1, tee_id=tee_front_red_f.id))
    session.add(Hole(number=4, par=4, yardage=333, stroke_index=13, tee_id=tee_front_red_f.id))
    session.add(Hole(number=5, par=3, yardage=170, stroke_index=9, tee_id=tee_front_red_f.id))
    session.add(Hole(number=6, par=4, yardage=325, stroke_index=17, tee_id=tee_front_red_f.id))
    session.add(Hole(number=7, par=4, yardage=282, stroke_index=11, tee_id=tee_front_red_f.id))
    session.add(Hole(number=8, par=3, yardage=90, stroke_index=15, tee_id=tee_front_red_f.id))
    session.add(Hole(number=9, par=5, yardage=410, stroke_index=5, tee_id=tee_front_red_f.id))
    session.commit()

    track_back = Track(name="Back", course_id=course.id)
    session.add(track_back)
    session.commit()

    tee_back_white_m = Tee(name="White", gender="M", rating=35.0, slope=126, color="white", track_id=track_back.id)
    session.add(tee_back_white_m)
    session.commit()

    session.add(Hole(number=10, par=3, yardage=184, stroke_index=4, tee_id=tee_back_white_m.id))
    session.add(Hole(number=11, par=5, yardage=530, stroke_index=6, tee_id=tee_back_white_m.id))
    session.add(Hole(number=12, par=3, yardage=192, stroke_index=10, tee_id=tee_back_white_m.id))
    session.add(Hole(number=13, par=4, yardage=430, stroke_index=2, tee_id=tee_back_white_m.id))
    session.add(Hole(number=14, par=5, yardage=488, stroke_index=12, tee_id=tee_back_white_m.id))
    session.add(Hole(number=15, par=4, yardage=399, stroke_index=14, tee_id=tee_back_white_m.id))
    session.add(Hole(number=16, par=4, yardage=340, stroke_index=18, tee_id=tee_back_white_m.id))
    session.add(Hole(number=17, par=3, yardage=180, stroke_index=8, tee_id=tee_back_white_m.id))
    session.add(Hole(number=18, par=5, yardage=510, stroke_index=16, tee_id=tee_back_white_m.id))
    session.commit()
    
    tee_back_gold_m = Tee(name="Gold", gender="M", rating=33.9, slope=115, color="gold", track_id=track_back.id)
    session.add(tee_back_gold_m)
    session.commit()

    session.add(Hole(number=10, par=3, yardage=155, stroke_index=4, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=11, par=5, yardage=475, stroke_index=6, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=12, par=3, yardage=181, stroke_index=10, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=13, par=4, yardage=407, stroke_index=2, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=14, par=5, yardage=482, stroke_index=12, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=15, par=4, yardage=377, stroke_index=14, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=16, par=4, yardage=235, stroke_index=18, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=17, par=3, yardage=163, stroke_index=8, tee_id=tee_back_gold_m.id))
    session.add(Hole(number=18, par=5, yardage=420, stroke_index=16, tee_id=tee_back_gold_m.id))
    session.commit()
    
    tee_back_red_f = Tee(name="Red", gender="F", rating=36.4, slope=128, color="red", track_id=track_back.id)
    session.add(tee_back_red_f)
    session.commit()

    session.add(Hole(number=10, par=3, yardage=100, stroke_index=18, tee_id=tee_back_red_f.id))
    session.add(Hole(number=11, par=5, yardage=465, stroke_index=6, tee_id=tee_back_red_f.id))
    session.add(Hole(number=12, par=3, yardage=166, stroke_index=16, tee_id=tee_back_red_f.id))
    session.add(Hole(number=13, par=5, yardage=390, stroke_index=2, tee_id=tee_back_red_f.id))
    session.add(Hole(number=14, par=5, yardage=476, stroke_index=8, tee_id=tee_back_red_f.id))
    session.add(Hole(number=15, par=4, yardage=357, stroke_index=10, tee_id=tee_back_red_f.id))
    session.add(Hole(number=16, par=4, yardage=230, stroke_index=12, tee_id=tee_back_red_f.id))
    session.add(Hole(number=17, par=3, yardage=125, stroke_index=14, tee_id=tee_back_red_f.id))
    session.add(Hole(number=18, par=5, yardage=410, stroke_index=4, tee_id=tee_back_red_f.id))
    session.commit()

def add_golfer(session: Session, name: str, affiliation: str):
    print(f"Adding golfer: {name}")
    session.add(Golfer(name=name, affiliation=affiliation))
    session.commit()

def add_flight(session: Session, name: str):
    print(f"Adding flight: {name}")
    flight = Flight(name=name, year=2021, home_course_id=1)
    session.add(flight)
    session.commit()

    session.add(Division(name="Middle", gender="M", flight_id=flight.id, home_tee_id=1))
    session.add(Division(name="Senior", gender="M", flight_id=flight.id, home_tee_id=2))
    session.add(Division(name="Forward", gender="F", flight_id=flight.id, home_tee_id=3))
    session.commit()

def add_team(session: Session, name: str):
    print(f"Added team: {name}")
    team = Team(name=name, flight_id=1)
    session.add(team)
    session.commit()

    session.add(Player(team_id=team.id, golfer_id=1, division_id=1, role="CAPTAIN"))
    session.add(Player(team_id=team.id, golfer_id=2, division_id=1, role="SUBSTITUTE"))
    session.add(Player(team_id=team.id, golfer_id=3, division_id=2, role="PLAYER"))
    session.add(Player(team_id=team.id, golfer_id=4, division_id=3, role="PLAYER"))
    session.commit()

def add_match(session: Session, flight_id: int, week: int, home_team_id: int, away_team_id: int, home_score: float = None, away_score: float = None):
    print(f"Adding week {week} match between team ids: {home_team_id}, {away_team_id}")
    session.add(Match(week=week, flight_id=flight_id, home_team_id=home_team_id, away_team_id=away_team_id, home_score=home_score, away_score=away_score))
    session.commit()

def add_round(session: Session, golfer_id: int, tee_id: int):
    print(f"Adding round: golfer_id={golfer_id}, tee_id={tee_id}")
    round = Round(golfer_id=golfer_id, tee_id=tee_id, handicap_index=12.3, playing_handicap=12, date_played=date.today())
    session.add(round)
    session.commit()

    session.add(HoleResult(round_id=round.id, hole_id=1, strokes=4))
    session.add(HoleResult(round_id=round.id, hole_id=2, strokes=5))
    session.add(HoleResult(round_id=round.id, hole_id=3, strokes=3))
    session.add(HoleResult(round_id=round.id, hole_id=4, strokes=5))
    session.add(HoleResult(round_id=round.id, hole_id=5, strokes=6))
    session.add(HoleResult(round_id=round.id, hole_id=6, strokes=5))
    session.add(HoleResult(round_id=round.id, hole_id=7, strokes=4))
    session.add(HoleResult(round_id=round.id, hole_id=8, strokes=4))
    session.add(HoleResult(round_id=round.id, hole_id=9, strokes=5))
    session.commit()

def add_match_round_link(session: Session, match_id: int, round_id: int):
    print(f"Linking match {match_id} with round {round_id}")
    session.add(MatchRoundLink(match_id=match_id, round_id=round_id))
    session.commit()

if __name__ == "__main__":
    DATABASE_FILE = "dev.db"

    if os.path.isfile(DATABASE_FILE):
        print(f"Removing existing database: {DATABASE_FILE}")
        os.remove(DATABASE_FILE)
    
    print(f"Initializing database: {DATABASE_FILE}")
    engine = create_engine(
        f"sqlite:///{DATABASE_FILE}", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)  

    with Session(engine) as session:
        add_course(session, "Diamond Ridge Golf Course")
        add_course(session, "Test Golf Course")

        add_golfer(session, "Andris Jaunzemis", "APL_EMPLOYEE")
        add_golfer(session, "George P. Burdell", "NON_APL_EMPLOYEE")
        add_golfer(session, "David Gibson", "APL_RETIREE")
        add_golfer(session, "Lily Jaunzemis", "APL_FAMILY")

        add_flight(session, "Diamond Ridge")

        add_team(session, "DR Team 1")
        add_team(session, "DR Team 2")

        add_match(session, 1, 1, 1, 2, 7.5, 3.5)
        add_match(session, 1, 2, 2, 1)

        add_round(session, 1, 1)
        add_round(session, 3, 2)

        add_match_round_link(session, 1, 1)
        add_match_round_link(session, 1, 2)

    print("Database initialized!")
