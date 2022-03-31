import os
from datetime import datetime
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine, select
from passlib.context import CryptContext

from models.course import Course
from models.track import Track
from models.tee import Tee, TeeGender
from models.hole import Hole
from models.golfer import Golfer, GolferAffiliation
from models.flight import Flight
from models.division import Division
from models.flight_division_link import FlightDivisionLink
from models.team import Team
from models.team_golfer_link import TeamGolferLink, TeamRole
from models.flight_team_link import FlightTeamLink
from models.match import Match
from models.round import Round
from models.round_golfer_link import RoundGolferLink
from models.hole_result import HoleResult
from models.match_round_link import MatchRoundLink
from models.tournament import Tournament
from models.tournament_division_link import TournamentDivisionLink
from models.tournament_team_link import TournamentTeamLink
from models.tournament_round_link import TournamentRoundLink
from models.officer import Officer
from models.payment import LeagueDues, LeagueDuesType, LeagueDuesPayment, TournamentEntryFeeType, TournamentEntryFeePayment
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def add_league_dues_fee(*, session: Session, year: int, type: LeagueDuesType, amount: float) -> LeagueDues:
    dues_fee_db = session.exec(select(LeagueDues).where(LeagueDues.year == year).where(LeagueDues.type == type)).one_or_none()
    if not dues_fee_db:
        print(f"Adding league dues fee: {type} ({year}) ${amount:.2f}")
        dues_fee_db = LeagueDues(year=year, type=type, amount=amount)
        session.add(dues_fee_db)
        session.commit()
    return dues_fee_db

def add_user(*, session: Session, username: str, name: str, email: str, password: str, disabled: bool) -> User:
    user_db = session.exec(select(User).where(User.username == username)).one_or_none()
    if not user_db:
        print(f"Adding user: {username}")
        user_db = User(
            username=username,
            name=name,
            email=email,
            hashed_password=pwd_context.hash(password),
            disabled=disabled
        )
        session.add(user_db)
        session.commit()

def add_diamond_ridge_course(*, session: Session) -> Course:
    dr_course_db = session.exec(select(Course).where(Course.name == "Diamond Ridge Golf Course")).one_or_none() # TODO: Add year filter: .where(Course.year == 2022)
    if not dr_course_db:
        print(f"Adding course: Diamond Ridge Golf Course (2022)")
        dr_course_db = Course(name="Diamond Ridge Golf Course", year=2022, location="123 Test Location, Some City, MD, 12345", phone="123-456-7890", website="google.com")
        session.add(dr_course_db)
        session.commit()

    dr_front_track_db = session.exec(select(Track).where(Track.course_id == dr_course_db.id).where(Track.name == "Front")).one_or_none()
    if not (dr_front_track_db):
        print(f"Adding track: Front")
        dr_front_track_db = Track(name="Front", course_id=dr_course_db.id)
        session.add(dr_front_track_db)
        session.commit()

    dr_front_white_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "White").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_front_white_mens_tee_db:
        print(f"Adding tee: White (Men's, Front)")
        dr_front_white_mens_tee_db = Tee(name="White", gender=TeeGender.MENS, rating=34.7, slope=126, color="white", track_id=dr_front_track_db.id)
        session.add(dr_front_white_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: White (Men's, Front)")
        session.add(Hole(number=1, par=4, yardage=383, stroke_index=7, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=2, par=4, yardage=383, stroke_index=5, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=3, par=4, yardage=429, stroke_index=1, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=4, par=4, yardage=359, stroke_index=11, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=5, par=3, yardage=197, stroke_index=3, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=6, par=4, yardage=345, stroke_index=9, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=7, par=4, yardage=314, stroke_index=13, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=8, par=3, yardage=146, stroke_index=17, tee_id=dr_front_white_mens_tee_db.id))
        session.add(Hole(number=9, par=5, yardage=492, stroke_index=15, tee_id=dr_front_white_mens_tee_db.id))
        session.commit()
    
    dr_front_gold_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Gold").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_front_gold_mens_tee_db:
        print(f"Adding tee: Gold (Men's, Front)")
        dr_front_gold_mens_tee_db = Tee(name="Gold", gender=TeeGender.MENS, rating=33.7, slope=117, color="gold", track_id=dr_front_track_db.id)
        session.add(dr_front_gold_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: Gold (Men's, Front)")
        session.add(Hole(number=1, par=4, yardage=372, stroke_index=7, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=2, par=4, yardage=363, stroke_index=5, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=3, par=4, yardage=415, stroke_index=1, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=4, par=4, yardage=346, stroke_index=11, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=5, par=3, yardage=175, stroke_index=3, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=6, par=4, yardage=330, stroke_index=9, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=7, par=4, yardage=287, stroke_index=13, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=8, par=3, yardage=100, stroke_index=17, tee_id=dr_front_gold_mens_tee_db.id))
        session.add(Hole(number=9, par=5, yardage=415, stroke_index=15, tee_id=dr_front_gold_mens_tee_db.id))
        session.commit()

    dr_front_red_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_front_red_mens_tee_db:
        print(f"Adding tee: Red (Men's, Front)")
        dr_front_red_mens_tee_db = Tee(name="Red", gender=TeeGender.MENS, rating=33.3, slope=115, color="red", track_id=dr_front_track_db.id)
        session.add(dr_front_red_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: Red (Ladies', Front)")
        session.add(Hole(number=1, par=4, yardage=353, stroke_index=3, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=2, par=4, yardage=348, stroke_index=7, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=3, par=5, yardage=401, stroke_index=1, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=4, par=4, yardage=333, stroke_index=13, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=5, par=3, yardage=170, stroke_index=9, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=6, par=4, yardage=325, stroke_index=17, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=7, par=4, yardage=282, stroke_index=11, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=8, par=3, yardage=90, stroke_index=15, tee_id=dr_front_red_mens_tee_db.id))
        session.add(Hole(number=9, par=5, yardage=410, stroke_index=5, tee_id=dr_front_red_mens_tee_db.id))
        session.commit()

    dr_front_red_ladies_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.LADIES)).one_or_none()
    if not dr_front_red_ladies_tee_db:
        print(f"Adding tee: Red (Ladies', Front)")
        dr_front_red_ladies_tee_db = Tee(name="Red", gender=TeeGender.LADIES, rating=35.9, slope=122, color="red", track_id=dr_front_track_db.id)
        session.add(dr_front_red_ladies_tee_db)
        session.commit()

        print(f"Adding holes for tee: Red (Ladies', Front)")
        session.add(Hole(number=1, par=4, yardage=353, stroke_index=3, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=2, par=4, yardage=348, stroke_index=7, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=3, par=5, yardage=401, stroke_index=1, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=4, par=4, yardage=333, stroke_index=13, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=5, par=3, yardage=170, stroke_index=9, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=6, par=4, yardage=325, stroke_index=17, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=7, par=4, yardage=282, stroke_index=11, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=8, par=3, yardage=90, stroke_index=15, tee_id=dr_front_red_ladies_tee_db.id))
        session.add(Hole(number=9, par=5, yardage=410, stroke_index=5, tee_id=dr_front_red_ladies_tee_db.id))
        session.commit()
        
    dr_back_track_db = session.exec(select(Track).where(Track.course_id == dr_course_db.id).where(Track.name == "Back")).one_or_none()
    if not (dr_back_track_db):
        print(f"Adding track: Back")
        dr_back_track_db = Track(name="Back", course_id=dr_course_db.id)
        session.add(dr_back_track_db)
        session.commit()

    dr_back_white_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "White").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_back_white_mens_tee_db:
        print(f"Adding tee: White (Men's, Back)")
        dr_back_white_mens_tee_db = Tee(name="White", gender=TeeGender.MENS, rating=35.4, slope=125, color="white", track_id=dr_back_track_db.id)
        session.add(dr_back_white_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: White (Men's, Back)")
        session.add(Hole(number=10, par=3, yardage=184, stroke_index=4, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=11, par=5, yardage=530, stroke_index=6, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=12, par=3, yardage=192, stroke_index=10, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=13, par=4, yardage=430, stroke_index=2, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=14, par=5, yardage=488, stroke_index=12, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=15, par=4, yardage=399, stroke_index=14, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=16, par=4, yardage=340, stroke_index=18, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=17, par=3, yardage=180, stroke_index=8, tee_id=dr_back_white_mens_tee_db.id))
        session.add(Hole(number=18, par=5, yardage=510, stroke_index=16, tee_id=dr_back_white_mens_tee_db.id))
        session.commit()
    
    dr_back_gold_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Gold").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_back_gold_mens_tee_db:
        print(f"Adding tee: Gold (Men's, Back)")
        dr_back_gold_mens_tee_db = Tee(name="Gold", gender=TeeGender.MENS, rating=34.2, slope=112, color="gold", track_id=dr_back_track_db.id)
        session.add(dr_back_gold_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: Gold (Men's, Back)")
        session.add(Hole(number=10, par=3, yardage=155, stroke_index=4, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=11, par=5, yardage=475, stroke_index=6, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=12, par=3, yardage=181, stroke_index=10, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=13, par=4, yardage=407, stroke_index=2, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=14, par=5, yardage=482, stroke_index=12, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=15, par=4, yardage=377, stroke_index=14, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=16, par=4, yardage=235, stroke_index=18, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=17, par=3, yardage=163, stroke_index=8, tee_id=dr_back_gold_mens_tee_db.id))
        session.add(Hole(number=18, par=5, yardage=420, stroke_index=16, tee_id=dr_back_gold_mens_tee_db.id))
        session.commit()
    
    dr_back_red_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.MENS)).one_or_none()
    if not dr_back_red_mens_tee_db:
        print(f"Adding tee: Red (Men's, Back)")
        dr_back_red_mens_tee_db = Tee(name="Red", gender=TeeGender.MENS, rating=33.3, slope=103, color="red", track_id=dr_back_track_db.id)
        session.add(dr_back_red_mens_tee_db)
        session.commit()

        print(f"Adding holes for tee: Red (Men's, Back)")
        session.add(Hole(number=10, par=3, yardage=100, stroke_index=18, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=11, par=5, yardage=465, stroke_index=6, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=12, par=3, yardage=166, stroke_index=16, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=13, par=5, yardage=390, stroke_index=2, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=14, par=5, yardage=476, stroke_index=8, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=15, par=4, yardage=357, stroke_index=10, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=16, par=4, yardage=230, stroke_index=12, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=17, par=3, yardage=125, stroke_index=14, tee_id=dr_back_red_mens_tee_db.id))
        session.add(Hole(number=18, par=5, yardage=410, stroke_index=4, tee_id=dr_back_red_mens_tee_db.id))
        session.commit()
    
    dr_back_red_ladies_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.LADIES)).one_or_none()
    if not dr_back_red_ladies_tee_db:
        print(f"Adding tee: Red (Ladies', Back)")
        dr_back_red_ladies_tee_db = Tee(name="Red", gender=TeeGender.LADIES, rating=35.1, slope=114, color="red", track_id=dr_back_track_db.id)
        session.add(dr_back_red_ladies_tee_db)
        session.commit()

        print(f"Adding holes for tee: Red (Ladies', Back)")
        session.add(Hole(number=10, par=3, yardage=100, stroke_index=18, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=11, par=5, yardage=465, stroke_index=6, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=12, par=3, yardage=166, stroke_index=16, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=13, par=5, yardage=390, stroke_index=2, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=14, par=5, yardage=476, stroke_index=8, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=15, par=4, yardage=357, stroke_index=10, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=16, par=4, yardage=230, stroke_index=12, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=17, par=3, yardage=125, stroke_index=14, tee_id=dr_back_red_ladies_tee_db.id))
        session.add(Hole(number=18, par=5, yardage=410, stroke_index=4, tee_id=dr_back_red_ladies_tee_db.id))
        session.commit()

    return dr_course_db

def add_golfer(*, session: Session, name: str, affiliation: GolferAffiliation) -> Golfer:
    golfer_db = session.exec(select(Golfer).where(Golfer.name == name)).one_or_none()
    if not golfer_db:
        print(f"Adding golfer: {name}")
        golfer_db = Golfer(name=name, affiliation=affiliation)
        session.add(golfer_db)
        session.commit()
    return golfer_db

def add_flight(*, session: Session, name: str, year: int, course_id: int, logo_url: str, secretary: str, secretary_email: str, signup_start_date: datetime, signup_stop_date: datetime, start_date: datetime, weeks: int) -> Flight:
    flight_db = session.exec(select(Flight).where(Flight.name == name).where(Flight.year == year)).one_or_none()
    if not flight_db:
        print(f"Adding flight: {name} ({year})")
        flight_db = Flight(name=name, year=year, course_id=course_id, logo_url=logo_url, secretary=secretary, secretary_email=secretary_email, signup_start_date=signup_start_date, signup_stop_date=signup_stop_date, start_date=start_date, weeks=weeks)
        session.add(flight_db)
        session.commit()
    return flight_db

def add_division(*, session: Session, name: str, gender: TeeGender, primary_tee_id: int, secondary_tee_id: int, flight_id: int) -> Division:
    division_db = session.exec(select(Division).join(FlightDivisionLink, onclause=FlightDivisionLink.division_id == Division.id).where(FlightDivisionLink.flight_id == flight_id).where(Division.name == name).where(Division.gender == gender)).one_or_none()
    if not division_db:
        print(f"Adding division: {name} ({gender})")
        division_db = Division(name=name, gender=gender, primary_tee_id=primary_tee_id, secondary_tee_id=secondary_tee_id)
        session.add(division_db)
        session.commit()

        print(f"Linking division id={division_db.id} to flight id={flight_id}")
        flight_division_link_db = FlightDivisionLink(flight_id=flight_id, division_id=division_db.id)
        session.add(flight_division_link_db)
        session.commit()
    return division_db

def add_team(*, session: Session, name: str, flight_id: int) -> Team:
    team_db = session.exec(select(Team).join(FlightTeamLink, onclause=FlightTeamLink.team_id == Team.id).where(FlightTeamLink.flight_id == flight_id).where(Team.name == name)).one_or_none()
    if not team_db:
        print(f"Adding team: {name}")
        team_db = Team(name=name, flight_id=1)
        session.add(team_db)
        session.commit()

        print(f"Linking team id={team_db.id} to flight id={flight_id}")
        flight_team_link_db = FlightTeamLink(flight_id=flight_id, team_id=team_db.id)
        session.add(flight_team_link_db)
        session.commit()
    return team_db

def add_golfer_to_team(*, session: Session, golfer_id: int, team_id: int, role: TeamRole, division_id: int) -> TeamGolferLink:
    team_golfer_link_db = session.exec(select(TeamGolferLink).where(TeamGolferLink.team_id == team_id).where(TeamGolferLink.golfer_id == golfer_id)).one_or_none()
    if not team_golfer_link_db:
        print(f"Linking golfer id={golfer_id} to team id={team_id} with role={role}, division_id={division_id}")
        team_golfer_link_db = TeamGolferLink(team_id=team_id, golfer_id=golfer_id, division_id=division_id, role=role)
        session.add(team_golfer_link_db)
        session.commit()
    return team_golfer_link_db

def add_league_dues_payment_for_golfer(*, session: Session, golfer_id: int, year: int, type: LeagueDuesType, amount_due: float) -> LeagueDuesPayment:
    golfer_dues_payment_db = session.exec(select(LeagueDuesPayment).where(LeagueDuesPayment.golfer_id == golfer_id).where(LeagueDuesPayment.year == year)).one_or_none()
    if not golfer_dues_payment_db:
        print(f"Adding league dues payment entry for golfer id={golfer_id}")
        golfer_dues_payment_db = LeagueDuesPayment(golfer_id=golfer_id, year=year, type=type, amount_due=amount_due)
        session.add(golfer_dues_payment_db)
        session.commit()
    return golfer_dues_payment_db

def add_tournament_entry_fee_payment_for_golfer(*, session: Session, golfer_id = int, year: int, tournament_id: int, type: TournamentEntryFeeType, amount_due: float) -> TournamentEntryFeePayment:
    golfer_entry_fee_payment_db = session.exec(select(TournamentEntryFeePayment).where(TournamentEntryFeePayment.golfer_id == golfer_id).where(TournamentEntryFeePayment.year == year).where(TournamentEntryFeePayment.tournament_id == tournament_id)).one_or_none()
    if not golfer_entry_fee_payment_db:
        print(f"Adding tournament entry fee payment entry for golfer id={golfer_id}")
        golfer_entry_fee_payment_db = TournamentEntryFeePayment(golfer_id=golfer_id, year=year, tournament_id=tournament_id, type=type, amount_due=amount_due)
        session.add(golfer_entry_fee_payment_db)
        session.commit()
    return golfer_entry_fee_payment_db

def add_scheduled_matches(*, session: Session, flight: Flight):
    flight_team_links_db = session.exec(select(FlightTeamLink).where(FlightTeamLink.flight_id == flight.id)).all()
    if (not flight_team_links_db) or (len(flight_team_links_db) == 0):
        raise ValueError("Unable to find flight: " + flight.name + " (" + flight.year + ")")
    
    team_ids = [link.team_id for link in flight_team_links_db]

    if (flight.weeks == 19) and (len(team_ids) == 6):
        matchup_matrix = [ # 6 teams, 19 weeks
            [6, 5, 4, 3, 2, 1], # week 1
            [5, 4, 6, 2, 1 ,3], # week 2
            [4, 3, 2, 1, 6, 5], # week 3
            [3, 6, 1, 5, 4, 2], # week 4
            [2, 1, 5, 6, 3, 4], # week 5
            [6, 5, 4, 3, 2, 1], # week 6
            [None, None, None, None, None, None], # week 7
            [5, 4, 6, 2, 1, 3], # week 8
            [4, 3, 2, 1, 6, 5], # week 9
            [3, 6, 1, 5, 4, 2], # week 10
            [2, 1, 5, 6, 3, 4], # week 11
            [None, None, None, None, None, None], # week 12
            [6, 5, 4, 3, 2, 1], # week 13
            [5, 4, 6, 2, 1, 3], # week 14
            [4, 3, 2, 1, 6, 5], # week 15
            [3, 6, 1, 5, 4, 2], # week 16
            [2, 1, 5, 6, 3, 4], # week 17
            [6, 5, 4, 3, 2, 1], # week 18
            [6, 5, 4, 3, 2, 1], # week 19
        ]
    else:
        raise ValueError(f"No pre-defined {flight.weeks}-week matchup matrix for {len(team_ids)} teams")

    for week_idx in range(len(matchup_matrix)):
        week = week_idx + 1
        for team_idx in range(len(team_ids)):
            team_id = team_ids[team_idx]
            if matchup_matrix[week_idx][team_idx]: # check for byes
                opponent_team_id = team_ids[matchup_matrix[week_idx][team_idx] - 1]
                match_db = session.exec(select(Match).where(Match.flight_id == flight.id).where(Match.week == week).where(((Match.home_team_id == team_id) & (Match.away_team_id == opponent_team_id)) | (Match.home_team_id == opponent_team_id) & (Match.away_team_id == team_id))).one_or_none()
                if not match_db:
                    print(f"Adding match: week={week}, home_team_id={team_id}, away_team_id={opponent_team_id}")
                    match_db = Match(flight_id=flight.id, week=week, home_team_id=team_id, away_team_id=opponent_team_id)
                    session.add(match_db)
                    session.commit()

if __name__ == "__main__":
    UPDATE_MYSQL_DB = True # if false, overwrites local sqlite database

    if UPDATE_MYSQL_DB:
        load_dotenv()

        DATABASE_USER = os.environ.get("APLGL_DATABASE_USER")
        DATABASE_PASSWORD = os.environ.get("APLGL_DATABASE_PASSWORD")
        DATABASE_ADDRESS = os.environ.get("APLGL_DATABASE_ADDRESS")
        DATABASE_PORT = os.environ.get("APLGL_DATABASE_PORT")
        DATABASE_NAME = os.environ.get("APLGL_DATABASE_NAME")

        DATABASE_URL = f"mysql+mysqlconnector://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:{DATABASE_PORT}/{DATABASE_NAME}"
        
        print(f"Updating database: {DATABASE_NAME}")
        engine = create_engine(DATABASE_URL, echo=False)
    else: # use local sqlite database
        DATABASE_FILE = "dev.db"

        if os.path.isfile(DATABASE_FILE):
            print(f"Removing existing database: {DATABASE_FILE}")
            os.remove(DATABASE_FILE)
        
        print(f"Initializing database: {DATABASE_FILE}")
        engine = create_engine(f"sqlite:///{DATABASE_FILE}", connect_args={"check_same_thread": False})

    SQLModel.metadata.create_all(engine)  

    # with Session(engine) as session:
    #     # Add league dues
    #     add_league_dues_fee(session=session, year=2022, type=LeagueDuesType.FLIGHT_DUES, amount=40)
    #     add_league_dues_fee(session=session, year=2022, type=LeagueDuesType.TOURNAMENT_ONLY_DUES, amount=35)

    #     # Course and Tees
    #     dr_course_db = add_diamond_ridge_course(session=session)

    #     dr_front_track_db = session.exec(select(Track).where(Track.course_id == dr_course_db.id).where(Track.name == "Front")).one()
    #     dr_front_white_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "White").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_front_gold_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Gold").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_front_red_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_front_red_ladies_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_front_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.LADIES)).one()

    #     dr_back_track_db = session.exec(select(Track).where(Track.course_id == dr_course_db.id).where(Track.name == "Back")).one()
    #     dr_back_white_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "White").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_back_gold_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Gold").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_back_red_mens_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.MENS)).one()
    #     dr_back_red_ladies_tee_db = session.exec(select(Tee).where(Tee.track_id == dr_back_track_db.id).where(Tee.name == "Red").where(Tee.gender == TeeGender.LADIES)).one()

    #     # Golfers
    #     adj_golfer_db = add_golfer(session=session, name="Andris Jaunzemis", affiliation=GolferAffiliation.APL_EMPLOYEE)
    #     add_league_dues_payment_for_golfer(session=session, golfer_id=adj_golfer_db.id, year=2022, type=LeagueDuesType.FLIGHT_DUES, amount_due=40.00)
    #     sej_golfer_db = add_golfer(session=session, name="Samantha Jaunzemis", affiliation=GolferAffiliation.APL_FAMILY)
    #     add_league_dues_payment_for_golfer(session=session, golfer_id=sej_golfer_db.id, year=2022, type=LeagueDuesType.FLIGHT_DUES, amount_due=35.00)
    #     lgj_golfer_db = add_golfer(session=session, name="Lily Jaunzemis", affiliation=GolferAffiliation.APL_FAMILY)
    #     add_league_dues_payment_for_golfer(session=session, golfer_id=lgj_golfer_db.id, year=2022, type=LeagueDuesType.TOURNAMENT_ONLY_DUES, amount_due=30.00)
    #     add_tournament_entry_fee_payment_for_golfer(session=session, golfer_id=lgj_golfer_db.id, year=2022, tournament_id=1, type=TournamentEntryFeeType.MEMBER_FEE, amount_due=60.00)
        
    #     gpb_golfer_db = add_golfer(session=session, name="George P. Burdell", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     mt_golfer_db = add_golfer(session=session, name="Merel Tuve", affiliation=GolferAffiliation.APL_RETIREE)
    #     na_golfer_db = add_golfer(session=session, name="Neil Armstrong", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)

    #     tw_golfer_db = add_golfer(session=session, name="Tiger Woods", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     pm_golfer_db = add_golfer(session=session, name="Phil Mickelson", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     rm_golfer_db = add_golfer(session=session, name="Rory McIlroy", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     js_golfer_db = add_golfer(session=session, name="Jordan Spieth", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     jt_golfer_db = add_golfer(session=session, name="Justin Thomas", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     nk_golfer_db = add_golfer(session=session, name="Nelly Korda", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)

    #     jl_golfer_db = add_golfer(session=session, name="John Landshof", affiliation=GolferAffiliation.APL_EMPLOYEE)
    #     be_golfer_db = add_golfer(session=session, name="Bob Erlandson", affiliation=GolferAffiliation.APL_EMPLOYEE)
    #     rs_golfer_db = add_golfer(session=session, name="Richie Steinwand", affiliation=GolferAffiliation.APL_EMPLOYEE)

    #     ms_golfer_db = add_golfer(session=session, name="Michael Scott", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     jh_golfer_db = add_golfer(session=session, name="Jim Halpert", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     ph_golfer_db = add_golfer(session=session, name="Pam Halpert", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     ds_golfer_db = add_golfer(session=session, name="Dwight Schrute", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     cb_golfer_db = add_golfer(session=session, name="Creed Bratton", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)

    #     ca_golfer_db = add_golfer(session=session, name="Captain America", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     im_golfer_db = add_golfer(session=session, name="Iron Man", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     bw_golfer_db = add_golfer(session=session, name="Black Widow", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     sm_golfer_db = add_golfer(session=session, name="Spiderman", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)
    #     he_golfer_db = add_golfer(session=session, name="Hawkeye", affiliation=GolferAffiliation.NON_APL_EMPLOYEE)

    #     # Flight and Divisions
    #     tf_flight_db = add_flight(session=session, name="Test Flight", year=2022, course_id=dr_course_db.id, logo_url="apl_golf_logo.png", secretary="Andris Jaunzemis", secretary_email="adjaunzemis@gmail.com", signup_start_date=datetime(2022, 3, 1, 0, 0, 0), signup_stop_date=datetime(2022, 4, 1, 0, 0, 0), start_date=datetime(2022, 4, 18, 0, 0, 0), weeks=19)

    #     tf_middle_mens_division_db = add_division(session=session, name="Middle", gender=TeeGender.MENS, primary_tee_id=dr_front_white_mens_tee_db.id, secondary_tee_id=dr_back_white_mens_tee_db.id, flight_id=tf_flight_db.id)
    #     tf_senior_mens_division_db = add_division(session=session, name="Senior", gender=TeeGender.MENS, primary_tee_id=dr_front_gold_mens_tee_db.id, secondary_tee_id=dr_back_gold_mens_tee_db.id, flight_id=tf_flight_db.id)
    #     tf_supersenior_mens_division_db = add_division(session=session, name="Super-Senior", gender=TeeGender.MENS, primary_tee_id=dr_front_red_mens_tee_db.id, secondary_tee_id=dr_back_red_mens_tee_db.id, flight_id=tf_flight_db.id)
    #     tf_forward_ladies_division_db = add_division(session=session, name="Forward", gender=TeeGender.LADIES, primary_tee_id=dr_front_red_ladies_tee_db.id, secondary_tee_id=dr_back_red_ladies_tee_db.id, flight_id=tf_flight_db.id)

    #     # Teams
    #     jaunzemax_team_db = add_team(session=session, name="JaunzeMAX", flight_id=tf_flight_db.id)

    #     add_golfer_to_team(session=session, golfer_id=lgj_golfer_db.id, team_id=jaunzemax_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_forward_ladies_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=adj_golfer_db.id, team_id=jaunzemax_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=sej_golfer_db.id, team_id=jaunzemax_team_db.id, role=TeamRole.PLAYER, division_id=tf_forward_ladies_division_db.id)

    #     legends_team_db = add_team(session=session, name="Legends", flight_id=tf_flight_db.id)

    #     add_golfer_to_team(session=session, golfer_id=gpb_golfer_db.id, team_id=legends_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=mt_golfer_db.id, team_id=legends_team_db.id, role=TeamRole.PLAYER, division_id=tf_supersenior_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=na_golfer_db.id, team_id=legends_team_db.id, role=TeamRole.PLAYER, division_id=tf_senior_mens_division_db.id)

    #     pros_team_db = add_team(session=session, name="Pros", flight_id=tf_flight_db.id)

    #     add_golfer_to_team(session=session, golfer_id=tw_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=pm_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=rm_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=js_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=jt_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=nk_golfer_db.id, team_id=pros_team_db.id, role=TeamRole.PLAYER, division_id=tf_forward_ladies_division_db.id)

    #     committee_team_db = add_team(session=session, name="The Committee", flight_id=tf_flight_db.id)
        
    #     add_golfer_to_team(session=session, golfer_id=jl_golfer_db.id, team_id=committee_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=be_golfer_db.id, team_id=committee_team_db.id, role=TeamRole.PLAYER, division_id=tf_senior_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=rs_golfer_db.id, team_id=committee_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)

    #     dunder_team_db = add_team(session=session, name="Dunder Mifflin", flight_id=tf_flight_db.id)
        
    #     add_golfer_to_team(session=session, golfer_id=ms_golfer_db.id, team_id=dunder_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=jh_golfer_db.id, team_id=dunder_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=ph_golfer_db.id, team_id=dunder_team_db.id, role=TeamRole.PLAYER, division_id=tf_forward_ladies_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=ds_golfer_db.id, team_id=dunder_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=cb_golfer_db.id, team_id=dunder_team_db.id, role=TeamRole.PLAYER, division_id=tf_supersenior_mens_division_db.id)

    #     avengers_team_db = add_team(session=session, name="Avengers", flight_id=tf_flight_db.id)

    #     add_golfer_to_team(session=session, golfer_id=ca_golfer_db.id, team_id=avengers_team_db.id, role=TeamRole.CAPTAIN, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=im_golfer_db.id, team_id=avengers_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=bw_golfer_db.id, team_id=avengers_team_db.id, role=TeamRole.PLAYER, division_id=tf_forward_ladies_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=sm_golfer_db.id, team_id=avengers_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
    #     add_golfer_to_team(session=session, golfer_id=he_golfer_db.id, team_id=avengers_team_db.id, role=TeamRole.PLAYER, division_id=tf_middle_mens_division_db.id)
        
    #     # Add matches to set flight schedule
    #     add_scheduled_matches(session=session, flight=tf_flight_db)

    # print("Database updates complete!")
