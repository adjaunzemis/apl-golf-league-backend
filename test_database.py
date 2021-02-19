r"""
Test script for database interactions

Authors
-------
Andris Jaunzemis

"""

from apl_golf_league_database import APLGolfLeagueDatabase
from golf_models import *

def load_diamond_ridge():
    VERBOSE = False
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=VERBOSE)
    course = db.get_course("Diamond Ridge Golf Course", "Front", "middle", "M", verbose=VERBOSE)
    print(course.as_dict())

def load_timbers():
    VERBOSE = False
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=VERBOSE)
    course = db.get_course("Timbers at Troy Golf Course", "Front", "middle", "M", verbose=VERBOSE)
    print(course.as_dict())

if __name__ == "__main__":
    load_diamond_ridge()
    load_timbers()
    