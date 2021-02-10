r"""
Processing script for match data files

Authors
-------
Andris Jaunzemis

"""

import re
import pandas as pd
from datetime import date, datetime

def parse_match_data_from_file(file):
    matches = []
    matchFound = False
    matchLines = []
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            if not matchFound:
                if (len(line) > 5) and (line[:5].lower() == 'match'):
                    matchFound = True
                    matchLines = [line,]
            else:
                if len(line) > 1:
                    matchLines.append(line)
                else:
                    matches.append(matchLines.copy())
                    matchFound = False
                    matchLines = []
    return matches

def match_data_to_dict(match_data):
    match_dict = dict()

    # Parse matchup overview from first line
    #   MATCH <week> <team1> vs <team2> <score1> to <score2> on <date_played> at <course> 0
    if (len(match_data[0]) < 6) or (match_data[0][:5].lower() != "match"):
        raise ValueError("First line must be matchup overview and start with MATCH")
    
    matchup_parts = [matchup_part.strip() for matchup_part in match_data[0].split() if matchup_part.strip() != '']
    
    match_dict['week'] = int(matchup_parts[1])
    match_dict['team_1'] = int(matchup_parts[2])
    match_dict['team_2'] = int(matchup_parts[4])
    match_dict['team_1_score'] = float(matchup_parts[5])
    match_dict['team_2_score'] = float(matchup_parts[7])
    match_dict['date_played'] = datetime.strptime(matchup_parts[9], '%b-%d-%Y').date()
    match_dict['course_abbreviation'] = matchup_parts[11]

    # Parse data entry timestamp from second line
    #   DATE_ENTERED <month> <day>, <year> at <hour>:<minute> <AM/PM>
    if (len(match_data[1]) < 12) or (match_data[1][:12].lower() != "date_entered"):
        raise ValueError("Second line must be date entered and start with DATE_ENTERED")

    date_entered_parts = [line_part.strip() for line_part in match_data[1].split() if line_part.strip() != '']
    
    if date_entered_parts[5][:2] == '0:': # handle 12th-hour bug (stored as "0:" instead of "12:")
        date_entered_parts[5] = "12:{:s}".format(date_entered_parts[3][2:])

    date_entered_str = "{0:s}-{1:s}{2:s} {3:s} {4:s}".format(date_entered_parts[1], date_entered_parts[2], date_entered_parts[3], date_entered_parts[5], date_entered_parts[6])
    match_dict['date_entered'] = datetime.strptime(date_entered_str, '%B-%d,%Y %I:%M %p')

    # Parse round data from third through sixth lines
    #   ROUND, <date_played>, <week>, <name>, <hole_1_score>, ..., <hole_9_score>, <gross_score>, <adj_gross_score>, <handicap>, <score_differential>
    playerNum = 0
    for round_data in match_data[2:]:
        playerNum += 1

        round_parts = [round_part.strip() for round_part in re.split(',', round_data) if round_part.strip() != '']
        
        match_dict['p' + str(playerNum) + '_date_played'] = datetime.strptime(round_parts[1], '%b-%d-%Y').date()
        match_dict['p' + str(playerNum) + '_week'] = int(round_parts[2])
        match_dict['p' + str(playerNum) + '_name'] = round_parts[3]
        for hole_num in range(1, 10):
            match_dict['p' + str(playerNum) + '_h' + str(hole_num) + '_score'] = int(round_parts[3 + hole_num])
        match_dict['p' + str(playerNum) + '_gross_score'] = int(round_parts[13])
        match_dict['p' + str(playerNum) + '_adj_gross_score'] = int(round_parts[14])
        match_dict['p' + str(playerNum) + '_handicap'] = int(round_parts[15])
        match_dict['p' + str(playerNum) + '_score_differential'] = float(round_parts[16])

    return match_dict

if __name__ == "__main__":
    match_data_list = parse_match_data_from_file("data/scores.tat.data")

    match_dict_list = []
    for match_data in match_data_list:
        match_dict_list.append(match_data_to_dict(match_data))

    csv_data = ",".join([str(k) for k,v in match_dict_list[0].items()])
    for match_dict in match_dict_list:
        csv_data += "\n" + ",".join([str(v) for k,v in match_dict.items()])

    with open("data/scores_tat_processed.csv", "w") as fp:
        fp.write(csv_data)
        