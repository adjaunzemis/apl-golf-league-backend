r"""
Processing script for roster data files

Authors
-------
Andris Jaunzemis

"""

def parse_roster_data_from_file(file):
    players = []
    currentTeam = -1
    currentCourse = ""
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            if line[:4].lower() == 'team':
                currentTeam = int(line.split()[1])
            elif line[:9].lower() == 'preferred':
                currentCourse = " ".join(line.split()[1:])
            elif line[:6].lower() == 'golfer':
                # Parse player information
                #   GOLFER <first_name> <last_name> <location> <phone> <?> <email> <tees> <classification> <employee_id>
                line_parts = line.split()
                if len(line_parts) != 10:
                    raise ValueError("Unable to parse roster player line: {:s}".format(line))

                player = {
                    'name': " ".join(line_parts[1:3]),
                    'team': currentTeam,
                    'course': currentCourse,
                    'location': line_parts[3],
                    'phone': line_parts[4],
                    'other': line_parts[5],
                    'email': line_parts[6],
                    'tees': line_parts[7],
                    'classification': line_parts[8],
                    'employee_id': line_parts[9]
                }
                players.append(player)
    return players

if __name__ == "__main__":
    DATA_YEAR = 2019
    ROSTER_DATA_FILES = ["roster.dr.data", "roster.fh.data", "roster.nwp.data", "roster.rw.data", "roster.tat.data", "roster.playoffs.data"]

    for roster_data_file in ROSTER_DATA_FILES:
        print("Processing {:d} roster data file: {:s}".format(DATA_YEAR, roster_data_file))

        roster_dict_list = parse_roster_data_from_file("data/{:s}".format(roster_data_file))

        csv_data = ",".join([str(k) for k,v in roster_dict_list[0].items()])
        for match_dict in roster_dict_list:
            csv_data += "\n" + ",".join([str(v) for k,v in match_dict.items()])

        course_abbreviation = roster_data_file.split(".")[1]
        outputFile = "data/roster_{:s}_{:d}.csv".format(roster_data_file.split(".")[1], DATA_YEAR)
        with open(outputFile, "w") as fp:
            fp.write(csv_data)
        