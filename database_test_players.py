r"""
Script to initialize players and player_contacts tables in database

Authors
-------
Andris Jaunzemis

"""

import pandas as pd

from golf_player import GolfPlayer
from golf_player_contact import GolfPlayerContact
from apl_golf_league_database import APLGolfLeagueDatabase


def init_db():
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    return APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

def test_mock_players():
    # Create list of mock players
    players = []

    burdell = GolfPlayer(
        last_name = "Burdell",
        first_name = "George",
        middle_name = "P",
        affiliation = "UNKNOWN"
    )
    burdell.add_contact(GolfPlayerContact(type="Email", contact="gpburdell@gatech.edu"))
    players.append(burdell)

    andris = GolfPlayer(
        last_name = "Jaunzemis",
        first_name = "Andris",
        middle_name = "Davis",
        affiliation = "APL_EMPLOYEE"
    )
    andris.add_contact(GolfPlayerContact(type="Phone", contact="x22088"))
    andris.add_contact(GolfPlayerContact(type="Email", contact="Andris.Jaunzemis@jhuapl.edu"))
    andris.add_contact(GolfPlayerContact(type="Office", contact="200-E342"))
    players.append(andris)

    samantha = GolfPlayer(
        last_name = "Jaunzemis",
        first_name = "Samantha",
        middle_name = "Elizabeth",
        affiliation = "APL_FAMILY_MEMBER"
    )
    players.append(samantha)

    mickelson = GolfPlayer(
        last_name = "Mickelson",
        first_name = "Phil",
        affiliation = "NON_APL_EMPLOYEE"
    )
    mickelson.add_contact(GolfPlayerContact(type="Phone", contact="123-456-7890"))
    players.append(mickelson)

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
