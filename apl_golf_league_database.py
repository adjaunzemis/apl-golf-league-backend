r"""
APL Golf League Database

Authors
-------
Andris Jaunzemis

"""

import json
import mysql.connector

from golf_models import GolfCourse, GolfHole, GolfFlight

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

    def get_all_course_names(self, verbose=False):
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

    def get_course_id(self, course_name, track_name, tee_name, gender, verbose=False):
        r"""
        Fetches course identifier for the course matching the given parameters.

        If a matching course cannot be found in the database, returns None.

        Parameters
        ----------
        course_name : string
            course name
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
            if matching course not found, returns None

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

        # Return matched course id or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def get_course(self, course_name, track_name, tee_name, gender, verbose=False):
        r"""
        Fetches golf course data for the course matching the given parameters.

        If a matching course cannot be found in the database, returns None.

        Parameters
        ----------
        course_name : string
            course name
        track_name : string
            9-hole track name
        tee_name : string
            tee set name
        gender : string
            indicates whether men's or women's data is requested
            Options: "M", "F"
        verbose : boolean, optional
            if true, prints details to console
        
        Returns
        -------
        hole : GolfHole
            golf hole data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT abbreviation, rating, slope, tee_color, address, city, state, zip_code, phone, website FROM courses WHERE course_name='{:s}' AND track_name='{:s}' AND tee_name='{:s}' AND gender='{:s}';".format(course_name, track_name, tee_name, gender)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return None if matching course not found
        if len(data) == 0:
            return None

        # Process query result into course
        result = data[0]
        course = GolfCourse(course_name, track_name, result[0], tee_name, gender, result[1], result[2])
        # TODO: Add other (optional) data fields from query
        
        # Gather hole data for this course
        course_id = self.get_course_id(course_name, track_name, tee_name, gender, verbose=verbose)
        hole_numbers = self.get_hole_numbers_for_course(course_id, verbose=verbose)

        for hole_number in hole_numbers:
            hole = self.get_hole(course_id, hole_number, verbose=verbose)
            course.add_hole(hole.number, hole.par, hole.handicap, hole.yardage)
            # TODO: Add ability to add hole object directly to course

        # Return course
        return course
    
    def put_course(self, course, update=False, verbose=False):
        r"""
        Adds/updates golf course data in database, populating 'courses' table.
        
        Also loops through golf holes to populate 'course_holes' table.

        Parameters
        ----------
        course : GolfCourse
            golf course data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
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

        # Check if course already exists in database
        course_id = self.get_course_id(course.course_name, course.track_name, course.tee_name, course.gender, verbose=verbose)
        if course_id is None:
            # Build course insert query
            query = course._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Course '{:s}' already exists in database, id={:d}".format(str(course), course_id))

            # Build course update query
            query = course._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add/update course data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve course id for this course
        course_id = self.get_course_id(course.course_name, course.track_name, course.tee_name, course.gender, verbose=verbose)
        if verbose:
            print("Added/updated course '{:s}' (id={:d}) in courses table".format(str(course), course_id))

        # Build and execute query to add each hole
        for hole in course.holes:
            self.put_hole(hole, course_id, update=update, verbose=verbose)

    def get_hole(self, course_id, number, verbose=False):
        r"""
        Fetches golf hole data for the hole matching the given parameters.

        If a matching hole cannot be found in the database, returns None.

        Parameters
        ----------
        course_id : int
            course identifier
        number : int
            hole number
        verbose : boolean, optional
            if true, prints details to console
        
        Returns
        -------
        hole : GolfHole
            golf hole data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT par, handicap, yardage FROM course_holes WHERE course_id={:d} AND number={:d};".format(course_id, number)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched golf hole or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return GolfHole(number, result[0], result[1], result[2])

    def get_hole_id(self, course_id, number, verbose=False):
        r"""
        Fetches golf hole identifier for hole matching given parameters.

        If no matching golf hole is found, returns None.

        Parameters
        ----------
        course_id : int
            course identifier
        number : int
            hole number
        verbose : boolean, optional
            if true, prints details to console
        
        Returns
        -------
        id : int
            golf hole identifier from database
            if matching course not found, returns None

        """
        # Build query
        query = "SELECT id FROM course_holes WHERE course_id={:d} AND number={:d};".format(course_id, number)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched hole id or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]
        
    def get_hole_numbers_for_course(self, course_id, verbose=False):
        r"""
        Fetches golf hole numbers for the given golf course.

        Parameters
        ----------
        course_id : int
            course identifier
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        Returns
        -------
        numbers : list-like of ints
            golf hole numbers for this course

        """
        # Build query
        query = "SELECT number FROM course_holes WHERE course_id = {:d};".format(course_id)
        
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        return [d[0] for d in data]

    def put_hole(self, hole, course_id, update=False, verbose=False):
        r"""
        Adds/updates golf course hole data in database, populating 'course_holes' table.

        Parameters
        ----------
        hole : GolfHole
            golf hole data to add
        course_id : int
            course identifer associated with this hole
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        # Check if hole already exists in database
        hole_id = self.get_hole_id(course_id, hole.number, verbose=verbose)
        if hole_id is None:
            # Build hole insert query
            query = hole._create_database_insert_query(course_id)
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Hole #{:d} for course id={:d} already exists in database, id={:d}".format(hole.number, course_id, hole_id))

            # Build hole update query
            query = hole._create_database_update_query(course_id)

        if verbose:
            print("Executing query: {:s}".format(query))
        
        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()
        
        if verbose:
            print("Added/updated hole #{:d} for course id={:d} to course_holes table".format(hole.number, course_id))

    def get_flight(self, name, year, verbose=False):
        r"""
        Fetches golf league flight data for the flight matching the given parameters.

        If a matching flight cannot be found in the database, returns None.

        Parameters
        ----------
        name : string
            flight name
        year : int
            flight year
        verbose : boolean, optional
            if true, prints details to console
        
        Returns
        -------
        flight : GolfFlight
            golf league flight data
            if no match is found, returns None

        """
        # Build query
        query = "SELECT abbreviation, mens_course_id, senior_course_id, super_senior_course_id, womens_course_id FROM flights WHERE name='{:s}' AND year={:d};".format(name, year)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched golf flight or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return GolfFlight(name, year, result[0], result[1], result[2], result[3], result[4])

    def get_flight_id(self, name, year, update=False, verbose=False):
        r"""
        Fetches flight identifier for the flight matching the given parameters.

        If a matching flight cannot be found in the database, returns None.

        Parameters
        ----------
        name : string
            flight name
        year : int
            flight year
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        flight_id : int
            golf league flight identifier from database
            if matching flight not found, returns None

        """
        # Build query
        query = "SELECT id FROM flights WHERE name='{:s}' AND year={:d};".format(name, year)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched flight id or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_flight(self, flight: GolfFlight, update=False, verbose=False):
        r"""
        Adds/updates golf course hole data in database, populating 'course_holes' table.

        Parameters
        ----------
        flight : GolfFlight
            golf flight data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        # Check if flight already exists in database
        flight_id = self.get_flight_id(flight.name, flight.year, verbose=verbose)
        if flight_id is None:
            # Build flight insert query
            query = flight._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Flight '{:s}' already exists in database, id={:d}".format(str(flight), flight_id))

            # Build flight update query
            query = flight._create_database_update_query(flight_id)

        if verbose:
            print("Executing query: {:s}".format(query))
        
        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()
        
        if verbose:
            print("Added/updated flight '{:s}' to flights table".format(str(flight)))
