r"""
Script to initialize flights table in database

TODO: Automate this further using the <flight>.info flat files.

Authors
-------
Andris Jaunzemis

"""

from golf_models import GolfFlight
from apl_golf_league_database import APLGolfLeagueDatabase

def init_diamond_ridge():
    r"""
    Initialize Diamond Ridge flight for 2019.
    
    See file: dr.info

    """
    db = APLGolfLeagueDatabase("config/admin.user", verbose=True)

    mens_course_id = db.get_course_id("Diamond Ridge Golf Course", "Front", "middle", "M", verbose=False)
    senior_course_id = db.get_course_id("Diamond Ridge Golf Course", "Front", "senior", "M", verbose=False)
    super_senior_course_id = db.get_course_id("Diamond Ridge Golf Course", "Front", "supersenior", "M", verbose=False)
    womens_course_id = db.get_course_id("Diamond Ridge Golf Course", "Front", "forward", "M", verbose=False) # TODO: Fix gender of 'forward' tees

    dr_flight = GolfFlight("Diamond Ridge", 2019, "DR", mens_course_id, senior_course_id, super_senior_course_id, womens_course_id)
    print(dr_flight.as_dict())

    db.put_flight(dr_flight, update=True, verbose=True)

def init_timbers_at_troy():
    r"""
    Initialize Timbers at Troy flight for 2019.
    
    See file: tat.info

    """
    db = APLGolfLeagueDatabase("config/admin.user", verbose=True)

    mens_course_id = db.get_course_id("Timbers at Troy Golf Course", "Front", "middle", "M", verbose=False)
    senior_course_id = db.get_course_id("Timbers at Troy Golf Course", "Front", "senior", "M", verbose=False)
    super_senior_course_id = db.get_course_id("Timbers at Troy Golf Course", "Front", "supersenior", "M", verbose=False)
    womens_course_id = db.get_course_id("Timbers at Troy Golf Course", "Front", "forward", "M", verbose=False) # TODO: Fix gender of 'forward' tees

    tat_flight = GolfFlight("Timbers at Troy", 2019, "DR", mens_course_id, senior_course_id, super_senior_course_id, womens_course_id)
    print(tat_flight.as_dict())

    db.put_flight(tat_flight, update=True, verbose=True)

if __name__ == "__main__":
    init_diamond_ridge()
    init_timbers_at_troy()
