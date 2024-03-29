r"""
Processing script for old tournament data files.

Authors
-------
Andris Jaunzemis

"""

import os
from datetime import datetime, time, timedelta

import pandas as pd


def parse_tournament_info_file(file: str, year: int):
    info = {
        "name": None,
        "abbreviation": None,
        "in_charge": None,
        "in_charge_email": None,
        "date": None,
        "signup_start_date": None,
        "signup_stop_date": None,
        "course": None,
        "front_track": None,
        "back_track": None,
        "shotgun": None,
        "strokeplay": None,
        "bestball": None,
        "scramble": None,
        "ryder_cup": None,
        "individual": None,
        "chachacha": None,
        "softspikes": None,
    }
    with open(file, "r") as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(",", " ")
            if (len(line) > 0) and (
                line[0].lower() != "#"
            ):  # skip empty and comment lines
                line_parts = line.split()
                if len(line_parts) > 1:
                    if line_parts[0].lower() == "tournament":
                        info["name"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == "nickname":
                        info["abbreviation"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == "in_charge":
                        if not info["in_charge"]:
                            info["in_charge"] = " ".join(line_parts[1:3])
                            info["in_charge_email"] = line_parts[4]
                    elif line_parts[0].lower() == "date":
                        date_str = f"{year}-{line_parts[1][:3]}-{line_parts[2]}"
                        try:
                            info["date"] = datetime.strptime(
                                date_str, "%Y-%b-%d"
                            ).date()
                        except:
                            raise ValueError(
                                "Unable to parse tournament date: " + date_str
                            )
                    elif line_parts[0].lower() == "signup_begins":
                        info["signup_start_date"] = info["date"] - timedelta(
                            days=int(line_parts[-1])
                        )
                    elif line_parts[0].lower() == "signup_ends":
                        info["signup_stop_date"] = info["date"] - timedelta(
                            days=int(line_parts[-1])
                        )
                    elif line_parts[0].lower() == "start_time":
                        info["start_time"] = datetime.strptime(
                            line_parts[-1], "%H:%M"
                        ).time()
                        if info["start_time"] < time(7, 0):
                            info["start_time"] = (
                                datetime.strptime(line_parts[-1], "%H:%M")
                                + timedelta(hours=12)
                            ).time()
                    elif line_parts[0].lower() == "course":
                        info["course"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == "front_nick":
                        info["front_track"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == "back_nick":
                        info["back_track"] = " ".join(line_parts[1:])
                    elif line_parts[0].lower() == "shotgun":
                        info["shotgun"] = (
                            True if line_parts[1].lower() == "on" else False
                        )
                    elif line_parts[0].lower() == "strokeplay":
                        info["strokeplay"] = (
                            True if line_parts[1].lower() == "on" else False
                        )
                    elif line_parts[0].lower() == "bestball":
                        info["bestball"] = (
                            True if line_parts[1].lower() == "on" else False
                        )
                    elif line_parts[0].lower() == "scramble":
                        info["scramble"] = (
                            True if line_parts[1].lower() == "on" else False
                        )
                    elif line_parts[0].lower() == "ryder_cup":
                        info["ryder_cup"] = (
                            True if line_parts[1].lower() == "on" else False
                        )
    return info


def check_tournament_played(info: dict, year: int, custom_tournaments_file: str):
    df_custom = pd.read_csv(custom_tournaments_file)
    for idx, row in df_custom.iterrows():
        if (row["year"] == year) and (row["name"].lower() == info["name"].lower()):
            return True
    return False


def parse_tournament_roster_file(file: str):
    roster = []
    with open(file, "r") as fp:
        group_num = -1
        for line in fp:
            line = line.strip()
            line = line.replace(",", " ")
            if (len(line) > 0) and (
                line[0].lower() != "#"
            ):  # skip empty and comment lines
                line_parts = line.split()
                if len(line_parts) > 1:
                    if line_parts[0].lower() == "group":
                        group_num = int(line_parts[1])
                    elif line_parts[0].lower() == "golfer":
                        if len(line_parts) > 2:
                            tees_index = line_parts.index("TEES")
                            name = " ".join(line_parts[1:tees_index])
                            tees = line_parts[tees_index + 1]
                            roster.append(
                                {"group": group_num, "name": name, "tees": tees}
                            )
    return roster


def parse_tournament_scores_file(file: str):
    scores = []
    with open(file, "r") as fp:
        for line in fp:
            line = line.strip()
            if (len(line) > 0) and (
                line[0].lower() != "#"
            ):  # skip empty and comment lines
                line_parts = line.split(",")
                if len(line_parts) > 1:
                    line_name = line_parts[1].strip()
                    if line_name[:6].lower() != "group ":
                        scores.append(
                            {
                                "group": int(line_parts[0]),
                                "name": line_name,
                                "course_handicap": int(line_parts[2]),
                                "hole_1": int(line_parts[3]),
                                "hole_2": int(line_parts[4]),
                                "hole_3": int(line_parts[5]),
                                "hole_4": int(line_parts[6]),
                                "hole_5": int(line_parts[7]),
                                "hole_6": int(line_parts[8]),
                                "hole_7": int(line_parts[9]),
                                "hole_8": int(line_parts[10]),
                                "hole_9": int(line_parts[11]),
                                "hole_10": int(line_parts[12]),
                                "hole_11": int(line_parts[13]),
                                "hole_12": int(line_parts[14]),
                                "hole_13": int(line_parts[15]),
                                "hole_14": int(line_parts[16]),
                                "hole_15": int(line_parts[17]),
                                "hole_16": int(line_parts[18]),
                                "hole_17": int(line_parts[19]),
                                "hole_18": int(line_parts[20]),
                                "front_gross": int(line_parts[21]),
                                "back_gross": int(line_parts[22]),
                                "total_gross": int(line_parts[23]),
                                "front_adj_gross": int(line_parts[24]),
                                "back_adj_gross": int(line_parts[25]),
                            }
                        )
    return scores


def parse_tournament_scores_summary_file(file: str):
    scores = []
    with open(file, "r") as fp:
        for line in fp:
            line = line.strip()
            line = line.replace(",", " ")
            if (len(line) > 0) and (
                line[0].lower() != "#"
            ):  # skip empty and comment lines
                line_parts = line.split()
                if (len(line_parts) > 1) and (
                    line_parts[-1].lower() != "net"
                ):  # skip table header
                    name = " ".join(line_parts[0:-3])
                    gross = int(line_parts[-3])
                    handicap = int(line_parts[-2])
                    net = int(line_parts[-1])
                    scores.append(
                        {"name": name, "gross": gross, "handicap": handicap, "net": net}
                    )
    return scores


def parse_tournament_results_file(file: str):
    results = []
    with open(file, "r") as fp:
        category = None
        for line in fp:
            line = line.strip()
            line = line.replace(",", " ")
            if (len(line) > 0) and (
                line[0].lower() != "#"
            ):  # skip empty and comment lines
                line_parts = line.split()
                if (len(line_parts) > 1) and (
                    line_parts[0].lower() != "hole"
                ):  # skip table column headers
                    if line_parts[0].isdigit():
                        results.append(
                            {
                                "category": category,
                                "hole": int(line_parts[0]),
                                "name": " ".join(line_parts[1:3]),
                                "details": (
                                    None
                                    if len(line_parts) < 4
                                    else " ".join(line_parts[3:])
                                ),
                            }
                        )
                    else:
                        category = " ".join(line_parts)
    return results


if __name__ == "__main__":
    CUSTOM_TOURNAMENTS_FILE = "data/tournaments_custom.csv"
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        # Process tournament info files
        info_files = [
            f
            for f in os.listdir(f"data/{data_dir}/Tournaments/")
            if (len(f) > 5)
            and (f[-5:] == ".info")
            and (f.lower() != "empty.info")
            and (f.lower() != "template.info")
        ]
        info_output_file = f"data/tournaments_{data_year}.csv"
        info_dict_list = []
        for info_file in info_files:
            print(f"Processing {data_year} tournament info file: {info_file}")

            try:
                info_dict = parse_tournament_info_file(
                    f"data/{data_dir}/Tournaments/{info_file}", data_year
                )
                if check_tournament_played(
                    info=info_dict,
                    year=data_year,
                    custom_tournaments_file=CUSTOM_TOURNAMENTS_FILE,
                ):
                    info_dict_list.append(info_dict)
            except:
                print("\tERROR: Unable to process tournament info file!")

        if len(info_dict_list) == 0:
            print(f"No tournament info data to output for year={data_year}")
        else:
            info_csv_data = ",".join([str(k) for k, v in info_dict_list[0].items()])
            for info_dict in info_dict_list:
                info_csv_data += "\n" + ",".join([str(v) for k, v in info_dict.items()])

            print(f"Writing processed tournament info data to file: {info_output_file}")
            with open(info_output_file, "w") as fp:
                fp.write(info_csv_data)

        for info_dict in info_dict_list:
            # Process tournament roster
            roster_file = f"{info_dict['abbreviation']}.teeinfo"
            print(f"Processing {data_year} tournament roster file: {roster_file}")

            roster = []
            try:
                roster = parse_tournament_roster_file(
                    f"data/{data_dir}/Tournaments/{roster_file}"
                )
            except:
                print("\tERROR: Unable to process tournament roster file!")

            if len(roster) == 0:
                print("\tNo tournament roster data to output")
            else:
                roster_csv_data = ",".join([str(k) for k, v in roster[0].items()])
                for roster_entry in roster:
                    roster_csv_data += "\n" + ",".join(
                        [str(v) for k, v in roster_entry.items()]
                    )

                roster_output_file = f"data/tournament_roster_{data_year}_{info_dict['abbreviation']}.csv"
                print(
                    f"\tWriting processed tournament roster data to file: {roster_output_file}"
                )
                with open(roster_output_file, "w") as fp:
                    fp.write(roster_csv_data)

            # Process tournament scores
            scores_file = f"{info_dict['abbreviation']}.scores"
            print(f"Processing {data_year} tournament scores file: {scores_file}")

            scores = []
            try:
                scores = parse_tournament_scores_file(
                    f"data/{data_dir}/Tournaments/{scores_file}"
                )
            except:
                print("\tERROR: Unable to process tournament scores file!")

            if len(scores) == 0:
                print("\tNo tournament scores data to output")
            else:
                scores_csv_data = ",".join([str(k) for k, v in scores[0].items()])
                for scores_entry in scores:
                    scores_csv_data += "\n" + ",".join(
                        [str(v) for k, v in scores_entry.items()]
                    )

                scores_output_file = f"data/tournament_scores_{data_year}_{info_dict['abbreviation']}.csv"
                print(
                    f"\tWriting processed tournament scores data to file: {scores_output_file}"
                )
                with open(scores_output_file, "w") as fp:
                    fp.write(scores_csv_data)

            # Process tournament gross scores summary
            gross_scores_file = f"{info_dict['abbreviation']}.gross"
            print(
                f"Processing {data_year} tournament gross scores file: {gross_scores_file}"
            )

            gross_scores = []
            try:
                gross_scores = parse_tournament_scores_summary_file(
                    f"data/{data_dir}/Tournaments/{gross_scores_file}"
                )
            except:
                print("\tERROR: Unable to process tournament gross scores file!")

            if len(gross_scores) == 0:
                print("\tNo tournament gross scores data to output")
            else:
                gross_scores_csv_data = ",".join(
                    [str(k) for k, v in gross_scores[0].items()]
                )
                for gross_scores_entry in gross_scores:
                    gross_scores_csv_data += "\n" + ",".join(
                        [str(v) for k, v in gross_scores_entry.items()]
                    )

                gross_scores_output_file = (
                    f"data/tournament_gross_{data_year}_{info_dict['abbreviation']}.csv"
                )
                print(
                    f"\tWriting processed tournament gross scores data to file: {gross_scores_output_file}"
                )
                with open(gross_scores_output_file, "w") as fp:
                    fp.write(gross_scores_csv_data)

            # Process tournament net scores summary
            net_scores_file = f"{info_dict['abbreviation']}.net"
            print(
                f"Processing {data_year} tournament net scores file: {net_scores_file}"
            )

            net_scores = []
            try:
                net_scores = parse_tournament_scores_summary_file(
                    f"data/{data_dir}/Tournaments/{net_scores_file}"
                )
            except:
                print("\tERROR: Unable to process tournament net scores file!")

            if len(net_scores) == 0:
                print("\tNo tournament net scores data to output")
            else:
                net_scores_csv_data = ",".join(
                    [str(k) for k, v in net_scores[0].items()]
                )
                for net_scores_entry in net_scores:
                    net_scores_csv_data += "\n" + ",".join(
                        [str(v) for k, v in net_scores_entry.items()]
                    )

                net_scores_output_file = (
                    f"data/tournament_net_{data_year}_{info_dict['abbreviation']}.csv"
                )
                print(
                    f"\tWriting processed tournament net scores data to file: {net_scores_output_file}"
                )
                with open(net_scores_output_file, "w") as fp:
                    fp.write(net_scores_csv_data)

            # Process tournament results (winners, prizes, etc.)
            results_file = f"{info_dict['abbreviation']}.results"
            print(f"Processing {data_year} tournament results file: {results_file}")

            results = []
            try:
                results = parse_tournament_results_file(
                    f"data/{data_dir}/Tournaments/{results_file}"
                )
            except ValueError:
                print("\tERROR: Unable to process tournament results file!")

            if len(results) == 0:
                print("\tNo tournament results data to output")
            else:
                results_csv_data = ",".join([str(k) for k, v in results[0].items()])
                for results_entry in results:
                    results_csv_data += "\n" + ",".join(
                        [str(v) for k, v in results_entry.items()]
                    )

                results_output_file = f"data/tournament_results_{data_year}_{info_dict['abbreviation']}.csv"
                print(
                    f"\tWriting processed tournament results data to file: {results_output_file}"
                )
                with open(results_output_file, "w") as fp:
                    fp.write(results_csv_data)
