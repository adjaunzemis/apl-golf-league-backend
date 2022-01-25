r"""
Processing script for old tournament data files.

Authors
-------
Andris Jaunzemis

"""

from datetime import date, datetime
import os

def parse_tournament_info_file(file: str, year: int):
    info = {"name": None, "abbreviation": None, "in_charge": None, "in_charge_email": None,
        "date": None, "course": None, "front_track": None, "back_track": None, "shotgun": None,
        "strokeplay": None, "bestball": None, "scramble": None, "ryder_cup": None, "individual": None,
        "chachacha": None, "softspikes": None}
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#'): # skip empty and comment lines
                line_parts = line.split()
                if (len(line_parts) > 1):
                    if line_parts[0].lower() == 'tournament':
                        info["name"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == 'nickname':
                        info["abbreviation"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == 'in_charge':
                        if not info["in_charge"]:
                            info["in_charge"] = " ".join(line_parts[1:3])
                            info["in_charge_email"] = line_parts[4]
                    elif line_parts[0].lower() == 'date':
                        try:
                            info["date"] = datetime.strptime(f'{year}-{line_parts[1]}-{line_parts[2]}', "%Y-%B-%d")
                        except:
                            try:
                                info["date"] = datetime.strptime(f'{year}-{line_parts[1]}-{line_parts[2]}', "%Y-%b-%d")
                            except:
                                info["date"] =f'{year}-{line_parts[1]}-{line_parts[2]}'
                    elif line_parts[0].lower() == 'course':
                        info["course"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == 'front_nick':
                        info["front_track"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == 'back_nick':
                        info["back_track"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == 'shotgun':
                        info["shotgun"] = True if line_parts[1].lower() == 'on' else False
                    elif line_parts[0].lower() == 'strokeplay':
                        info["strokeplay"] = True if line_parts[1].lower() == 'on' else False
                    elif line_parts[0].lower() == 'bestball':
                        info["bestball"] = True if line_parts[1].lower() == 'on' else False
                    elif line_parts[0].lower() == 'scramble':
                        info["scramble"] = True if line_parts[1].lower() == 'on' else False
                    elif line_parts[0].lower() == 'ryder_cup':
                        info["ryder_cup"] = True if line_parts[1].lower() == 'on' else False
    return info

def parse_tournament_tee_info_file(file: str):
    # TODO: Implement parsing of tournament tee sheet
    pass

if __name__ == "__main__":
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        # Process tournament info files
        info_files = [f for f in os.listdir(f"data/{data_dir}/Tournaments/") if (len(f) > 5) and (f[-5:] == ".info") and (f.lower() != "empty.info") and (f.lower() != "template.info")]
        output_file = f"data/tournaments_{data_year}.csv"
        info_dict_list = []
        for info_file in info_files:
            print(f"Processing {data_year} tournament info file: {info_file}")

            try:
                info_dict_list.append(parse_tournament_info_file(f"data/{data_dir}/Tournaments/{info_file}", data_year))
                # TODO: Check for valid data (e.g. populated tee sheet) before adding to info list
            except ValueError:
                print("\tERROR: Unable to process tournament info file!")
            
        if len(info_dict_list) == 0:
            print(f"No tournament info data to output for year={data_year}")
        else:
            csv_data = ",".join([str(k) for k,v in info_dict_list[0].items()])
            for info_dict in info_dict_list:
                csv_data += "\n" + ",".join([str(v) for k,v in info_dict.items()])

            print(f"Writing processed data to file: {output_file}")
            with open(output_file, "w") as fp:
                fp.write(csv_data)

        # TODO: Process tournament tee sheets

        # TODO: Process tournament scores

        # TODO: Process tournament results (winners, prizes, etc.)
        