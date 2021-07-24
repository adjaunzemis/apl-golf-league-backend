r"""
Script to initialize players and player_contacts tables in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_player import GolfPlayer
from apl_golf_league_database import APLGolfLeagueDatabase


def init_db():
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    return APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

def test_mock_players():
    # Create list of mock players
    players = [
        GolfPlayer(
            last_name = "Burdell",
            first_name = "George",
            middle_name = "P",
            affiliation = "UNKNOWN"
        ),
        GolfPlayer(
            last_name = "Jaunzemis",
            first_name = "Andris",
            middle_name = "Davis",
            affiliation = "APL_EMPLOYEE"
        ),
        GolfPlayer(
            last_name = "Jaunzemis",
            first_name = "Samantha",
            middle_name = "Elizabeth",
            affiliation = "APL_FAMILY_MEMBER"
        ),
        GolfPlayer(
            last_name = "Mickelson",
            first_name = "Phil",
            affiliation = "NON_APL_EMPLOYEE"
        )
    ]

    # Initialize database connection
    db = init_db()

    for player in players:
        # Display player data
        print(player)
        print(player.as_dict())

        # Add/update player in database
        db.put_player(player, update=True, verbose=True)

if __name__ == "__main__":
    test_mock_players()
