r"""
APL Golf League Database

Authors
-------
Andris Jaunzemis

"""

import json
import mysql.connector

from golf_models import GolfCourse, GolfHole

class APLGolfLeagueDatabase(object):
    r"""
    APL golf league database interaction.
    
    """

    def __init__(self, config_file, verbose=False):
        r"""
        Opens database connection using configuration file.

        Parameters
        ----------
        config_file : string
            path to database connection configuration file
        verbose : boolean, optional
            if true, prints details on authentication to console
            Default: False
        
        """
        with open(config_file) as fp:
            config = json.load(fp)
            self._connection = mysql.connector.connect(**config)
            # if log is not None:
            #     log.write(
            #         "Authenticated to database '{:s}' as user '{:s}'".format(config['database'], config['user']),
            #         prefixes=log_prefixes,
            #         verbose=verbose
            #     )
            # elif verbose:
            if verbose:
                print("Authenticated to database '{:s}' as user '{:s}'".format(config['database'], config['user']))

    def fetch_all_course_names(self, verbose=False):
        r"""
        Fetches all course names from courses table.

        Parameters
        ----------
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        query = "SELECT course_name FROM courses;"
        if verbose:
            print("Executing query: {:s}".format(query))

        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    def fetch_course_id(self, course_name, track_name, tee_name, gender, verbose=False):
        r"""
        Fetches course identifier for the course matching the given parameters.

        Parameters
        ----------
        course_name : string
            golf course name
        track_name : string
            9-hole track name
        tee_name : string
            tee set name
        gender : string
            indicates whether men's or women's data is requested
            Options: "M", "F"
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        course_id : int
            golf course identifier from database

        """
        # Build query
        query = "SELECT id FROM courses WHERE course_name='{:s}' AND track_name='{:s}' AND tee_name='{:s}' AND gender='{:s}';".format(course_name, track_name, tee_name, gender)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Check data for unique returned value
        if len(data) == 0:
            raise Exception("Unable to find matching course entry")
        return data[0][0]
    
    def add_course(self, course, verbose=False):
        r"""
        Adds golf course data to database, populating 'courses' and 'course_holes' tables.

        Parameters
        ----------
        course : GolfCourse
            golf course data to add
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        """
        # Check input data integrity before adding to database.
        if not isinstance(course, GolfCourse):
            raise Exception("Input must be a GolfCourse")
        if len(course.holes) != 9:
            raise Exception("Input GolfCourse must have exactly 9 holes")
        for hole in course.holes:
            if not isinstance(hole, GolfHole):
                raise Exception("Input GolfCourse must contain a list of GolfHoles")

        # Build query for course data
        query = "INSERT INTO courses " + course._create_database_query_payload()
        # TODO: Implement UPDATE query if course already exists
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add course data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve course id for newly added course
        course_id = self.fetch_course_id(course.course_name, course.track_name, course.tee_name, course.gender, verbose=verbose)
        if verbose:
            print("Added course '{:s}' (id={:d}) to courses table".format(str(course), course_id))

        # Build and execute query to add each hole
        for hole in course.holes:
            self.add_hole(hole, course_id, verbose=verbose)

    def add_hole(self, hole, course_id, verbose=False):
        r"""
        Adds golf course hole data to database, populating 'course_holes' table.

        Parameters
        ----------
        hole : GolfHole
            golf hole data to add
        course_id : int
            course identifer associated with this hole
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        # Build query for hole data
        query = "INSERT INTO course_holes " + hole._create_database_query_payload(course_id)
        # TODO: Implement UPDATE query if hole already exists
        if verbose:
            print("Executing query: {:s}".format(query))
        
        # Execute query to add hole data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()
        
        if verbose:
            print("Added hole #{:d} for course id={:d} to course_holes table".format(hole.number, course_id))


def create_test_course_woodholme():
    # Create course
    course = GolfCourse(
        "Woodholme Country Club",
        "Front",
        "WCCF",
        "Blue",
        "M",
        34.8,
        133
    )

    # Add holes
    course.add_hole(1, 4, 17, 325)
    course.add_hole(2, 5, 7, 529)
    course.add_hole(3, 3, 11, 167)
    course.add_hole(4, 4, 1, 401)
    course.add_hole(5, 3, 13, 186)
    course.add_hole(6, 4, 5, 404)
    course.add_hole(7, 4, 9, 337)
    course.add_hole(8, 4, 15, 306)
    course.add_hole(9, 4, 3, 366)

    return course

if __name__ == "__main__":
    CONFIG_FILE = "./config/admin.user"
    db = APLGolfLeagueDatabase(CONFIG_FILE, verbose=True)

    # Add Woodholme Country Club (blue tees, mens) to database
    db.add_course(create_test_course_woodholme(), verbose=True)

    # Check data in database
    course_names = db.fetch_all_course_names(verbose=True)
    print(course_names)

    course_id = db.fetch_course_id("Woodholme Country Club", "Front", "Blue", "M", verbose=True)
    print(course_id)
