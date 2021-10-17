r"""
Processing script for old roster data files.

Creates CSV files to support populating the following tables:
- golfer: name, affiliation
- team: name, flight_id
- player: team_id, golfer_id, division_id, role

Authors
-------
Andris Jaunzemis

"""

import os

def parse_roster_data_from_file(file: str):
    players = []
    currentTeam = -1
    currentCourse = ""
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line[:4].lower() == 'team':
                if line.split()[1].lower() == "subs":
                    currentTeam = 0
                elif line.split()[1].lower() == "togs":
                    currentTeam = -1
                else:
                    currentTeam = int(line.split()[1])
            elif line[:9].lower() == 'preferred':
                currentCourse = " ".join(line.split()[1:])
            elif line[:6].lower() == 'golfer':
                # Parse player information
                #   GOLFER <first_name> <last_name> <location> <phone> <?> <email> <tees> <affiliation> <employee_id>
                line_parts = line.split()
                if len(line_parts) != 10:
                    raise ValueError("Unable to parse roster player line: {:s}".format(line))

                player = {
                    'name': " ".join(line_parts[1:3]),
                    'team': currentTeam,
                    'course': currentCourse,
                    'office': line_parts[3],
                    'phone': line_parts[4],
                    'other': line_parts[5],
                    'email': line_parts[6],
                    'division': line_parts[7],
                    'affiliation': line_parts[8],
                    'employee_id': line_parts[9]
                }
                players.append(player)
    return players

if __name__ == "__main__":
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        roster_files = [f for f in os.listdir(f"data/{data_dir}") if f[0:7] == "roster."]
        for roster_file in roster_files:
            print(f"Processing {data_year} roster file: {roster_file}")

            flight_name = roster_file.split(".")[1]
            output_file = f"data/roster_{data_year}_{flight_name}.csv"

            roster_dict_list = []
            try:
                roster_dict_list = parse_roster_data_from_file(f"data/{data_dir}/{roster_file}")
            except ValueError:
                print("\tERROR: Unable to process roster file!")
            
            if len(roster_dict_list) == 0:
                print("\tNo roster data to output")
            else:
                csv_data = ",".join([str(k) for k,v in roster_dict_list[0].items()])
                for roster_dict in roster_dict_list:
                    csv_data += "\n" + ",".join([str(v) for k,v in roster_dict.items()])

                print(f"\tWriting processed data to file: {output_file}")
                with open(output_file, "w") as fp:
                    fp.write(csv_data)
        