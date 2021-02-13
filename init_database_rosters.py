r"""
Script to initialize players, teams, and team_players tables in database

Authors
-------
Andris Jaunzemis

"""

import numpy as np
import pandas as pd

from golf_models import GolfPlayer
from apl_golf_league_database import APLGolfLeagueDatabase

def extract_players_from_roster(file):
    # Read data from file
    df = pd.read_csv(file)

    # Gather list of players
    players = []
    for index, row in df.iterrows():
        name_parts = row['name'].split()
        classification = row['classification'].upper()
        if classification == 'RETIREE':
            classification = 'APL_RETIREE'
        email = row['email']
        players.append(GolfPlayer(" ".join(name_parts[:-1]), name_parts[-1], classification, email))

    # Return list of players
    return players

def add_players_to_database(players):
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

    # Add each player to database
    for player in players:
        db.put_player(player, update=True, verbose=True)

def extract_flight_id_from_roster(file):
    # Read data from file
    df = pd.read_csv(file)
    year = int(file.split("_")[2][:4])

    # Get flight identifier based on course in this roster
    course_name = np.unique(df['course'])
    if len(course_name) != 1:
        raise ValueError("Must be exactly one unique course name entry in roster file")
    course_name = course_name[0]
    print(course_name)
    
    # Initialize connection to database
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=False)

    # Find flight identifier
    flight_id = db.get_flight_id(course_name, year, verbose=False)
    if flight_id is None:
        raise ValueError("Unable to find flight at course '{:s}' in year={:d}")

    return flight_id

def extract_teams_from_roster(file):
    # Read data from file
    df = pd.read_csv(file)

    # Initialize teams
    team_numbers = np.unique(df['team'])
    print(team_numbers)
    
    # Organize players from roster into each team
    for team_number in team_numbers:
        data = df.loc[df['team'] == team_number]
        print(data)

def add_teams_to_database(team):
    print(team)
        
if __name__ == "__main__":
    ROSTER_SPREADSHEET_FILES = ['roster_tat_2019.csv']

    for roster_file in ROSTER_SPREADSHEET_FILES:
        roster_file_path = "data/{:s}".format(roster_file)
        print("Processing roster: {:s}".format(roster_file_path))

        # players = extract_players_from_roster(roster_file_path)
        # add_players_to_database(players)
        
        flight_id = extract_flight_id_from_roster(roster_file_path)
        teams = extract_teams_from_roster(roster_file_path)
        add_teams_to_database(teams, flight_id)
