r"""
Processing script for old tournament data files.

Authors
-------
Andris Jaunzemis

"""

import os

def parse_officer_info_file(file: str):
    info = []
    curCommittee = None
    isChair = True
    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(',', ' ')
            if (len(line) > 0) and (line[0].lower() != '#') and (line[0].lower() != "<"): # skip empty, comment, and tag lines
                line_parts = line.split()
                if (len(line_parts) > 0):
                    if line_parts[0].lower() == 'end':
                        curCommittee = None
                        isChair = True
                    elif line_parts[0].lower() == 'officers':
                        curCommittee = 'League'
                    elif line_parts[0].lower() == 'planning':
                        curCommittee = 'Planning'
                    elif line_parts[0].lower() == 'executive':
                        curCommittee = 'Executive'
                    elif line_parts[0].lower() == 'rules':
                        curCommittee = 'Rules'
                    elif line_parts[0].lower() == 'tournament':
                        curCommittee = 'Tournament'
                    elif line_parts[0].lower() == 'banquet/awards':
                        curCommittee = 'Banquet'
                    elif line_parts[0].lower() == 'publicity':
                        curCommittee = 'Publicity'
                    elif line_parts[0].lower() == 'flight':
                        curCommittee = 'Flights'
                    elif (line_parts[0].lower() != 'committees') and (line_parts[0].lower() != 'vacant'):
                        print(line_parts)
                        if curCommittee == 'League':
                            info.append({"committee": curCommittee, "role": line_parts[0], "name": " ".join(line_parts[1:3]), "room": line_parts[3], "phone": line_parts[4], "email": line_parts[5]})
                        else:
                            info.append({"committee": curCommittee, "role": "Chair" if isChair else "Member", "name": " ".join(line_parts[0:2]), "room": line_parts[2], "phone": line_parts[3], "email": line_parts[4]})
                        isChair = False
    return info

if __name__ == "__main__":
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        officers_files = [f for f in os.listdir(f"data/{data_dir}") if f[0:9] == "officers."]
        for officers_file in officers_files:
            print(f"Processing {data_year} officers file: {officers_file}")

            flight_name = officers_file.split(".")[1]
            output_file = f"data/officers_{data_year}.csv"

            officers_dict_list = []
            try:
                officers_dict_list = parse_officer_info_file(f"data/{data_dir}/{officers_file}")
            except ValueError:
                print("\tERROR: Unable to process officers file!")
            
            if len(officers_dict_list) == 0:
                print("\tNo officer data to output")
            else:
                csv_data = ",".join([str(k) for k,v in officers_dict_list[0].items()])
                for officer_dict in officers_dict_list:
                    csv_data += "\n" + ",".join([str(v) for k,v in officer_dict.items()])

                print(f"\tWriting processed data to file: {output_file}")
                with open(output_file, "w") as fp:
                    fp.write(csv_data)
