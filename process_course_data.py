r"""
Processing script for old course data files

Creates CSV files to support populating the following tables:
- course
- track
- tee
- hole

Authors
-------
Andris Jaunzemis

"""

import os
import numpy as np
import pandas as pd

def parse_course_data_from_file(file):
    courses = []

    curName = None
    curAddress = None
    curPhone = None
    curWebsite = None
    curTeeColors = None
    curTrackName = None
    curAbbreviation = None
    curPars = None
    curHandicaps = None

    with open(file, 'r') as fp:
        for line in fp:
            line = line.strip()
            if (len(line) > 4) and (line[0] != '#'):
                if line[:6].lower() == 'course':
                    if line[:17].lower() == 'course_parameters':
                        line_elements = line.split('#')[0].split()

                        front_name = line_elements[1]
                        front_course_matches = [course for course in courses if course['abbreviation'] == front_name]
                        if len(front_course_matches) != 1:
                            raise ValueError("Found {:d} course matches for front id={:s}".format(len(front_course_matches), front_name))
                        front_course = front_course_matches[0]
                        
                        back_name = line_elements[2]
                        back_course_matches = [course for course in courses if course['abbreviation'] == back_name]
                        if len(back_course_matches) != 1:
                            raise ValueError("Found {:d} course matches for back id={:s}".format(len(back_course_matches), back_name))
                        back_course = back_course_matches[0]
                        
                        front_par = np.sum(front_course['pars'])
                        back_par = np.sum(back_course['pars'])
                        total_par = front_par + back_par
                        
                        if len(line_elements) == 9:
                            # Slopes (mid, snr, fwd), Ratings (mid, snr, fwd)
                            front_course['tee_names'] = ['Middle', 'Senior', 'Forward']
                            front_course['ratings'] = [np.around(float(rating) * front_par / total_par, 2) for rating in line_elements[6:9]]
                            front_course['slopes'] = [int(slope) for slope in line_elements[3:6]]
                            
                            back_course['tee_names'] = ['Middle', 'Senior', 'Forward']
                            back_course['ratings'] = [np.around(float(rating) * back_par / total_par, 2) for rating in line_elements[6:9]]
                            back_course['slopes'] = [int(slope) for slope in line_elements[3:6]]
                        elif len(line_elements) == 11:
                            # Mid (slope, rating), Snr (slope, rating), Fwd (slope, rating), SupSnr (slope, rating)
                            front_course['tee_names'] = ['Middle', 'Senior', 'Forward', 'Super-Senior']
                            front_course['ratings'] = [np.around(float(rating) * front_par / total_par, 2) for rating in line_elements[4:11:2]]
                            front_course['slopes'] = [int(slope) for slope in line_elements[3:10:2]]
                            
                            back_course['tee_names'] = ['Middle', 'Senior', 'Forward', 'Super-Senior']
                            back_course['ratings'] = [np.around(float(rating) * back_par / total_par, 2) for rating in line_elements[4:11:2]]
                            back_course['slopes'] = [int(slope) for slope in line_elements[3:10:2]]
                    else:
                        if curTrackName is not None:
                            courses.append({
                                'course_name': curName,
                                'track_name': curTrackName,
                                'abbreviation': curAbbreviation,
                                'address': curAddress,
                                'phone': curPhone,
                                'website': curWebsite,
                                'tee_colors': curTeeColors,
                                'pars': curPars,
                                'handicaps': curHandicaps
                            })
                
                        curName = line[7:]
                        curAddress = None
                        curPhone = None
                        curWebsite = None
                        curTeeColors = None
                        curTrackName = None
                        curAbbreviation = None
                        curPars = None
                        curHandicaps = None
                
                elif line[:4].lower() == 'addr':
                    curAddress = line[5:]
                elif line[:6].lower() == 'colors':
                    curTeeColors = line[7:].split()
                elif line[:5].lower() == 'phone':
                    curPhone = line[6:]
                elif line[:3].lower() == 'url':
                    curWebsite = line[4:]
                elif line[:4].lower() == 'nine':
                    if line[4:9].lower() == '_name':
                        curTrackName = line[10:]
                    else:
                        curTrackName = None
                        curAbbreviation = None
                        curPars = None
                        curHandicaps = None

                        line_elements = line.split()

                        curAbbreviation = line_elements[1]
                        curPars = [int(val) for val in line_elements[-9:]]
                elif line[:8].lower() == 'handicap':
                    line_elements = line.split()
                    try:
                        curHandicaps = [int(val) for val in line_elements[-9:]]
                    except ValueError:
                        curHandicaps = [None for hole in range(9)]

            if not any([val is None for val in (curName, curAddress, curTrackName, curAbbreviation, curPars, curHandicaps)]):
                courses.append({
                    'course_name': curName,
                    'track_name': curTrackName,
                    'abbreviation': curAbbreviation,
                    'address': curAddress,
                    'phone': curPhone,
                    'website': curWebsite,
                    'tee_colors': curTeeColors,
                    'pars': curPars,
                    'handicaps': curHandicaps
                })

                curTrackName = None
                curPars = None
                curHandicaps = None
    return courses

def course_data_to_dict(course):
    name = course['course_name']
    track = course['track_name']
    abbreviation = course['abbreviation']
    address = course['address']
    phone = course['phone']
    website = course['website']

    if course['pars'] is None:
        pars = [None for idx in range(9)]
    else:
        pars = course['pars']

    if course['handicaps'] is None:
        handicaps = [None for idx in range(9)]
    else:
        handicaps = course['handicaps']
    
    if ('tee_names' not in course) or (course['tee_names'] is None):
        print(f"\tERROR: No tees for course {course['course_name']}")
        return None
    else:
        course_dicts = []
        for idx in range(len(course['tee_names'])):
            teeSet = course['tee_names'][idx]
            
            teeColor = None
            if course['tee_colors'] is not None:
                if (teeSet == "middle"):
                    teeColor = course['tee_colors'][0]
                if (teeSet == "senior"):
                    teeColor = course['tee_colors'][1]
                if (teeSet == "supersenior" or teeSet == "forward"):
                    teeColor = course['tee_colors'][2]

            rating = course['ratings'][idx]
            slope = course['slopes'][idx]

            # print(course['course_name'] + " " + course['track_name'] + ", tee_name=" + str(teeSet) + ", tee_color=" + str(teeColor) + ", rating=" + str(rating) + ", slope=" + str(slope))

            course_dicts.append({
                'course_name': name, 'track_name': track, 'abbreviation': abbreviation,
                'address': address, 'phone': phone, 'website': website,
                'tee_name': teeSet, 'tee_color': teeColor,
                'rating': rating, 'slope': slope,
                'par1': pars[0], 'hcp1': handicaps[0], 'yd1': None,
                'par2': pars[1], 'hcp2': handicaps[1], 'yd2': None,
                'par3': pars[2], 'hcp3': handicaps[2], 'yd3': None,
                'par4': pars[3], 'hcp4': handicaps[3], 'yd4': None,
                'par5': pars[4], 'hcp5': handicaps[4], 'yd5': None,
                'par6': pars[5], 'hcp6': handicaps[5], 'yd6': None,
                'par7': pars[6], 'hcp7': handicaps[6], 'yd7': None,
                'par8': pars[7], 'hcp8': handicaps[7], 'yd8': None,
                'par9': pars[8], 'hcp9': handicaps[8], 'yd9': None,
            })
        return course_dicts

if __name__ == "__main__":
    data_dirs = [f for f in os.listdir("data/") if f[0:10] == "golf_data."]
    for data_dir in data_dirs:
        data_year = 2000 + int(data_dir[-2:])

        course_files = [f for f in os.listdir(f"data/{data_dir}") if f == "apl.courses.data"]

        for course_file in course_files:
            print(f"Processing {data_year} courses file: {course_file}")

            course_data_list = parse_course_data_from_file(f"data/{data_dir}/{course_file}")

            course_dict_list = []
            for course_data in course_data_list:
                course_dicts = course_data_to_dict(course_data)
                if course_dicts is not None:
                    for course_dict in course_dicts:
                        course_dict_list.append(course_dict)

            outputFile = f"data/courses_{data_year}.csv"
            df = pd.DataFrame(course_dict_list)
            df.to_csv(outputFile, index=False)
