r"""
Processing script for old flight data files.

Creates CSV files to support populating the following tables:
- flight: name, year, home_course_id
- division: name, gender, flight_id, home_tee_id

Authors
-------
Andris Jaunzemis

"""

import os
from datetime import datetime

def parse_flight_data_from_file(file: str):
    flights = []
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#'): # skip empty and comment lines
                if line[:6].lower() == 'flight':
                    flights.append({
                        'abbreviation': line.split()[1],
                        'name': " ".join(line.split()[2:])
                    })
                elif line[:9].lower() == 'secretary':
                    flights[-1]["secretary"] = " ".join(line.split()[1:3])
                elif line[:6].lower() == 'course':
                    flights[-1]["home_track"] = " ".join(line.split()[1:])
                elif line[:5].lower() == 'teams':
                    flights[-1]["teams"] = int(line.split()[1])
                elif line[:4].lower() == 'type':
                    flights[-1]["type"] = " ".join(line.split()[1:])
    return flights

def parse_season_parameters(file: str):
    flight_dates = {}
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#'): # skip empty and comment lines
                line_parts = line.split()
                if line_parts[0].lower() == 'league_signup_date':
                    flight_dates['signup_start_date'] = datetime.strptime(" ".join(line_parts[1:]), "%B %d %Y")
                elif line_parts[0].lower() == 'end_league_signup_date':
                    flight_dates['signup_stop_date'] = datetime.strptime(" ".join(line_parts[1:]), "%B %d %Y")
                elif line_parts[0].lower() == 'league_start_date':
                    flight_dates['start_date'] = datetime.strptime(" ".join(line_parts[1:]), "%B %d %Y")
    return flight_dates

def parse_flight_schedule(abbreviation: str, data_dir: str):    
    flight_schedule_file = f"{data_dir}/{abbreviation}.sked"
    print(f"\tProcessing flight schedule file: {flight_schedule_file}")
    
    flight_schedule = {}
    with open(flight_schedule_file, 'r') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#'): # skip empty and comment lines
                line_parts = line.split()
                if (line_parts[0].lower() == 'tm') or (line_parts[0].lower() == 'team'):
                    flight_schedule['weeks'] = int(line_parts[-1])
                # TODO: Parse weekly schedule data
    return flight_schedule

def parse_flight_info(abbreviation: str, data_dir: str, signup_start_date: datetime, signup_stop_date: datetime, start_date: datetime, weeks: int):
    flight_info = {"course": None, "street": None, "citystzip": None, "clubpro": None, "director": None, "super": None, "phone": None, "link": None, "signup_start_date": signup_start_date, "signup_stop_date": signup_stop_date, "start_date": start_date, "weeks": weeks}
    
    flight_info_file = f"{data_dir}/{abbreviation}.info"
    print(f"\tProcessing flight info file: {flight_info_file}")

    divisions = []
    with open(flight_info_file) as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#'): #skip comment lines
                if line[:6].lower() == 'flight':
                    flight_info["flight"] = " ".join(line.split()[1:])
                elif line[:6].lower() == 'course':
                    flight_info["course"] = " ".join(line.split()[1:])
                elif line[:6].lower() == 'street':
                    flight_info["street"] = " ".join(line.split()[1:])
                elif line[:9].lower() == 'citystzip':
                    flight_info["citystzip"] = " ".join(line.split()[1:])
                elif line[:7].lower() == 'clubpro':
                    flight_info["clubpro"] = " ".join(line.split()[1:])
                elif line[:8].lower() == 'director':
                    flight_info["director"] = " ".join(line.split()[1:])
                elif line[:5].lower() == 'super':
                    flight_info["super"] = " ".join(line.split()[1:])
                elif line[:5].lower() == 'phone':
                    flight_info["phone"] = " ".join(line.split()[1:])
                elif line[:4].lower() == 'link':
                    flight_info["link"] = " ".join(line.split()[1:])
                elif line[:6].lower() == "middle":
                    divisions.append({"name": "middle", "tee": line.split()[1], "color1": line.split()[2], "color2": line.split()[3]})
                elif line[:6].lower() == "senior":
                    divisions.append({"name": "senior", "tee": line.split()[1], "color1": line.split()[2], "color2": line.split()[3]})
                elif line[:7].lower() == "forward":
                    divisions.append({"name": "forward", "tee": line.split()[1], "color1": line.split()[2], "color2": line.split()[3]})
                else:
                    print(f"WARNING: Unrecognized info line: {line}")

    # Reorganize division data
    dIdx = 0
    for division in divisions:
        dIdx += 1
        flight_info[f"division_{dIdx}_name"] = division["name"]
        flight_info[f"division_{dIdx}_tee"] = division["tee"]
        flight_info[f"division_{dIdx}_color1"] = division["color1"]
        flight_info[f"division_{dIdx}_color2"] = division["color2"]

    return flight_info

if __name__ == "__main__":
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        flight_files = [f for f in os.listdir(f"data/{data_dir}") if f == "apl.flights.data"]
        for flight_file in flight_files:
            print(f"Processing {data_year} flights file: {flight_file}")
            flight_dict_list = []
            try:
                flight_dict_list = parse_flight_data_from_file(f"data/{data_dir}/{flight_file}")
            except ValueError:
                print("\tERROR: Unable to process flight file!")

            print(f"Processing {data_year} season parameters file")
            try:
                flight_dates = parse_season_parameters(f"data/{data_dir}/season_parameters.data")
            except ValueError:
                print("\tERROR: Unable to process season parameters file!")
            
            if len(flight_dict_list) == 0:
                print("\tNo flight data to output")
            else:
                for flight_dict in flight_dict_list:
                    flight_schedule = parse_flight_schedule(abbreviation=flight_dict["abbreviation"], data_dir=f"data/{data_dir}")

                    flight_info = parse_flight_info(
                        abbreviation=flight_dict["abbreviation"],
                        data_dir=f"data/{data_dir}",
                        signup_start_date=flight_dates["signup_start_date"],
                        signup_stop_date=flight_dates["signup_stop_date"],
                        start_date=flight_dates["start_date"],
                        weeks=flight_schedule['weeks']
                    )
                    flight_dict.update(flight_info)

                csv_data = ",".join([str(k) for k,v in flight_dict_list[0].items()])
                for flight_dict in flight_dict_list:
                    csv_data += "\n" + ",".join([str(v) for k,v in flight_dict.items()])

                output_file = f"data/flights_{data_year}.csv"
                print(f"\tWriting processed data to file: {output_file}")
                with open(output_file, "w") as fp:
                    fp.write(csv_data)
        