r"""
APL Golf League Database

Authors
-------
Andris Jaunzemis

"""

import json
import mysql.connector

from golf_course import GolfCourse
from golf_track import GolfTrack
from golf_tee_set import GolfTeeSet
from golf_hole import GolfHole
from golf_models import GolfFlight, GolfPlayer, GolfTeam

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
        query = "SELECT name FROM courses;"
        if verbose:
            print("Executing query: {:s}".format(query))

        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_courses(self, course_id: int = None, name: str = None, city: str = None, state: str = None, verbose=False):
        r"""
        Fetches golf course data for courses matching the given parameters.

        Also calls 'get_tracks' to populate list of tracks for each course.

        If a matching course cannot be found in the database, returns None.

        Parameters
        ----------
        course_id : int, optional
            course identifier
            Default: None (not used in filtering database results)
        name : string, optional
            course name
            Default: None (not used in filtering database results)
        city : string, optional
            course city
            Default: None (not used in filtering database results)
        state : string, optional
            course state
            Default: None (not used in filtering database results)
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        courses : list of GolfCourses
            golf course data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT course_id, name, address, city, state, zip_code, phone, website, date_updated FROM courses"
        if any(val is not None for val in (course_id, name, city, state)):
            query += " WHERE"
            condition_count = 0
            if id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " id = {:d}".format(id)
            if name is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " name = '{:s}'".format(name)
            if city is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " city = '{:s}'".format(city)
            if state is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                state += " state = '{:s}'".format(state)

        query += ";"
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

        # Process query result into courses
        courses = []
        for course_data in data:
            course = GolfCourse(
                course_id=course_data[0],
                name=course_data[1]
            )
            course.address = course_data[3]
            course.city = course_data[4]
            course.state = course_data[5]
            course.zip_code = course_data[6]
            course.phone = course_data[7]
            course.website = course_data[8]
            course.date_updated = course_data[9]
            
            # Gather track data for this course
            course.tracks = self.get_tracks(course_id=course.course_id)

            # Add course to courses list
            courses.append(course)

        # Return courses
        return courses

    def get_course_id(self, name: str, city: str = None, state: str = None, verbose=False):
        r"""
        Fetches course identifier for the course matching the given parameters.

        If a matching course cannot be found in the database, returns None.

        Parameters
        ----------
        name : string
            course name
        city : string, optional
            course city
            Default: None (not used in filtering database results)
        state : string, optional
            course state
            Default: None (not used in filtering database results)
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
        query = "SELECT course_id FROM courses WHERE name='{:s}'".format(name)
        if city is not None:
            query += " AND city = '{:s}'".format(city)
        if state is not None:
            state += " AND state = '{:s}'".format(state)
        query += ";"
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched course id or None (if not found)
        # TODO: Handle condition where multiple matches are found?
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]
    
    def put_course(self, course: GolfCourse, update=False, verbose=False):
        r"""
        Adds/updates golf course data in database, populating 'courses' table.
        
        Also calls 'put_track' for each track in this golf course.

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
        
        Raises
        ------
        ValueError :
            if course already exists in database and 'update' is false

        """
        # Check input data integrity before adding to database.
        if not isinstance(course, GolfCourse):
            raise TypeError("Input must be a GolfCourse")

        # Check if course already exists in database
        course_id = self.get_course_id(course.name, city=course.city, state=course.state, verbose=verbose)
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

        # Retrieve course id for this course (if necessary)
        course_id = course.course_id
        if course_id is None:
            course_id = self.get_course_id(course.name, city=course.city, state=course.state, verbose=verbose)
        if verbose:
            print("Added/updated course '{:s}' (id={:d}) in courses table".format(str(course), course_id))

        # Build and execute queries to add tracks to database
        for track in course.tracks:
            if track.course_id is None:
                track.course_id = course_id
            self.put_track(track, update=update, verbose=verbose)

    def get_tracks(self, track_id: int = None, course_id: int = None, name: str = None, verbose=False):
        r"""
        Fetches golf course track data for tracks matching the given parameters.

        Also calls 'get_tee_sets' to populate list of tee sets for each track.

        If a matching track cannot be found in the database, returns None.

        Parameters
        ----------
        track_id : int, optional
            track identifier
            Default: None (not used in filtering database results)
        course_id : int, optional
            course identifier
            Default: None (not used in filtering database results)
        name : string, optional
            track name
            Default: None (not used in filtering database results)
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        tracks : list of GolfTracks
            golf course track data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT track_id, course_id, name, abbreviation FROM tracks"
        if any(val is not None for val in (track_id, course_id, name)):
            query += " WHERE"
            condition_count = 0
            if id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " track_id = {:d}".format(track_id)
            if course_id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " course_id = {:d}".format(course_id)
            if name is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " name = '{:s}'".format(name)

        query += ";"
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return None if matching track not found
        if len(data) == 0:
            return None

        # Process query result into tracks
        tracks = []
        for track_data in data:
            track = GolfTrack(
                track_id=track_data[0],
                course_id=track_data[1],
                name=track_data[2],
                abbreviation=track_data[3]
            )
            
            # Gather tee set data for this track
            track.tee_sets = self.get_tee_sets(track_id=track.track_id)

            # Append track to tracks list
            tracks.append(track)

        # Return tracks
        return tracks

    def get_track_id(self, course_id: int, name: str, verbose=False):
        r"""
        Fetches track identifier for the track matching the given parameters.

        If a matching track cannot be found in the database, returns None.

        Parameters
        ----------
        course_id : int
            course identifier
        name : string
            track name
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        track_id : int
            golf track identifier from database
            if matching track not found, returns None

        """
        # Build query
        query = "SELECT track_id FROM tracks WHERE course_id={:d} AND name='{:s}';".format(course_id, name)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched track id or None (if not found)
        # TODO: Handle condition where multiple matches are found?
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_track(self, track: GolfTrack, update=False, verbose=False):
        r"""
        Adds/updates golf course track in database, populating 'tracks' table.
        
        Also calls 'put_tee_set' for each tee set in this golf track.

        Parameters
        ----------
        track : GolfTrack
            golf course track data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Raises
        ------
        ValueError :
            if track already exists in database and 'update' is false
            
        """
        # Check input data integrity before adding to database.
        if not isinstance(track, GolfTrack):
            raise TypeError("Input must be a GolfTrack")

        # Check if track already exists in database
        track_id = self.get_track_id(track.course_id, track.name, verbose=verbose)
        if track_id is None:
            # Build track insert query
            query = track._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Track '{:s}' already exists in database, id={:d}".format(str(track), track_id))

            # Build track update query
            query = track._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add/update track data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve track id for this track (if necessary)
        track_id = track.track_id
        if track_id is None:
            track_id = self.get_track_id(track.course_id, track.name, verbose=verbose)
        if verbose:
            print("Added/updated track '{:s}' (id={:d}) in tracks table".format(str(track), track_id))

        # Build and execute queries to add tee sets to database
        for tee_set in track.tee_sets:
            if tee_set.track_id is None:
                tee_set.track_id = track_id
            self.put_tee_set(tee_set, update=update, verbose=verbose)

    def get_tee_sets(self, tee_set_id: int = None, track_id: int = None, name: str = None, gender: str = None, verbose=False):
        r"""
        Fetches golf tee set data for tee sets matching the given parameters.

        Also calls 'get_holes' to populate list of holes for each tee set.

        If a matching tee set cannot be found in the database, returns None.

        Parameters
        ----------
        tee_set_id : int, optional
            tee set identifier
            Default: None (not used in filtering database results)
        track_id : int, optional
            track identifier
            Default: None (not used in filtering database results)
        name : string, optional
            tee set name
            Default: None (not used in filtering database results)
        gender : string, optional
            tee set gender used for ratings and handicaps
            Options: 'M', 'F', None
            Default: None (not used in filtering database results)
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        tee_sets : list of GolfTeeSets
            golf tee set data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT tee_set_id, track_id, name, gender, rating, slope, color FROM tee_sets"
        if any(val is not None for val in (tee_set_id, track_id, name)):
            query += " WHERE"
            condition_count = 0
            if tee_set_id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " id = {:d}".format(tee_set_id)
            if track_id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " track_id = {:d}".format(track_id)
            if name is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " name = '{:s}'".format(name)
            if gender is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " gender = '{:s}'".format(gender)

        query += ";"
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return None if matching tee set not found
        if len(data) == 0:
            return None

        # Process query result into tee sets
        tee_sets = []
        for tee_set_data in data:
            tee_set = GolfTeeSet(
                tee_set_id=tee_set_data[0],
                track_id=tee_set_data[1],
                name=tee_set_data[2],
                gender=tee_set_data[3],
                rating=tee_set_data[4],
                slope=tee_set_data[5]
            )
            tee_set.color = tee_set_data[6]
            
            # Gather hole data for this tee set
            tee_set.holes = self.get_holes(tee_set_id=tee_set.tee_set_id)

            # Append tee set to tee set list
            tee_sets.append(tee_set)

        # Return tee sets
        return tee_sets

    def get_tee_set_id(self, track_id: int, name: str, gender: str, verbose=False):
        r"""
        Fetches tee set identifier for the tee set matching the given parameters.

        If a matching tee set cannot be found in the database, returns None.

        Parameters
        ----------
        track_id : int
            track identifier
        name : string
            tee set name
        gender : string
            tee set gender for rating and slope data
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        tee_set_id : int
            golf tee set identifier from database
            if matching tee set not found, returns None

        """
        # Build query
        query = "SELECT tee_set_id FROM tee_sets WHERE track_id={:d} AND name='{:s}' AND gender='{:s}';".format(track_id, name, gender)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched tee set id or None (if not found)
        # TODO: Handle condition where multiple matches are found?
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_tee_set(self, tee_set: GolfTeeSet, update=False, verbose=False):
        r"""
        Adds/updates golf course tee set in database, populating 'tee_sets' table.
        
        Also calls 'put_hole' for each hole in this golf tee set.

        Parameters
        ----------
        tee_set : GolfTeeSet
            golf course tee set data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Raises
        ------
        ValueError :
            if tee set already exists in database and 'update' is false
            
        """
        # Check input data integrity before adding to database.
        if not isinstance(tee_set, GolfTeeSet):
            raise TypeError("Input must be a GolfTeeSet")

        # Check if tee set already exists in database
        tee_set_id = self.get_tee_set_id(tee_set.track_id, tee_set.name, tee_set.gender, verbose=verbose)
        if tee_set_id is None:
            # Build tee set insert query
            query = tee_set._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Tee set '{:s}' already exists in database, id={:d}".format(str(tee_set), tee_set_id))

            # Build tee set update query
            query = tee_set._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add/update tee set data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve tee set id for this tee set (if necessary)
        tee_set_id = tee_set.tee_set_id
        if tee_set_id is None:
            tee_set_id = self.get_tee_set_id(tee_set.track_id, tee_set.name, tee_set.gender, verbose=verbose)
        if verbose:
            print("Added/updated tee set '{:s}' (id={:d}) in tee sets table".format(str(tee_set), tee_set_id))

        # Build and execute queries to add holes to database
        for hole in tee_set.holes:
            if hole.tee_set_id is None:
                hole.tee_set_id = tee_set_id
            self.put_hole(hole, update=update, verbose=verbose)

    def get_holes(self, hole_id: int = None, tee_set_id: int = None, number: int = None, verbose=False):
        r"""
        Fetches golf hole data for holes matching the given parameters.

        If a matching hole cannot be found in the database, returns None.

        Parameters
        ----------
        hole_id : int, optional
            hole identifier
            Default: None (not used in filtering database results)
        tee_set_id : int, optional
            tee set identifier
            Default: None (not used in filtering database results)
        number : int, optional
            hole number
            Default: None (not used in filtering database results)
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        holes : list of GolfHoles
            golf hole data
            if no match is found, returns None
        
        """
        # Build query
        query = "SELECT hole_id, tee_set_id, number, par, handicap, yardage FROM holes"
        if any(val is not None for val in (id, tee_set_id, number)):
            query += " WHERE"
            condition_count = 0
            if id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " hole_id = {:d}".format(hole_id)
            if tee_set_id is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " tee_set_id = {:d}".format(tee_set_id)
            if number is not None:
                condition_count += 1
                if condition_count > 1:
                    query += " AND"
                query += " number = {:d}".format(number)

        query += ";"
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return None if matching hole not found
        if len(data) == 0:
            return None

        # Process query result into holes
        holes = []
        for hole_data in data:
            hole = GolfHole(
                hole_id=hole_data[0],
                tee_set_id=hole_data[1],
                number=hole_data[2],
                par=hole_data[3],
                handicap=hole_data[4],
                yardage=hole_data[5]
            )

            # Append hole to holes list
            holes.append(hole)

        # Return holes
        return holes
    
    def get_hole_id(self, tee_set_id: int, number: int, verbose=False):
        r"""
        Fetches hole identifier for the hole matching the given parameters.

        If a matching hole cannot be found in the database, returns None.

        Parameters
        ----------
        tee_set_id : int
            tee set identifier
        number : int
            hole number
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        hole_id : int
            golf hole identifier from database
            if matching hole not found, returns None

        """
        # Build query
        query = "SELECT hole_id FROM holes WHERE tee_set_id={:d} AND number={:d};".format(tee_set_id, number)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched  hole id or None (if not found)
        # TODO: Handle condition where multiple matches are found?
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_hole(self, hole: GolfHole, update=False, verbose=False):
        r"""
        Adds/updates golf hole set in database, populating 'holes' table.

        Parameters
        ----------
        hole : GolfHole
            golf hole data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Raises
        ------
        ValueError :
            if hole already exists in database and 'update' is false
            
        """
        # Check input data integrity before adding to database.
        if not isinstance(hole, GolfHole):
            raise TypeError("Input must be a GolfHole")

        # Check if tee set already exists in database
        hole_id = self.get_hole_id(hole.tee_set_id, hole.number, verbose=verbose)
        if hole_id is None:
            # Build tee set insert query
            query = hole._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Hole '{:s}' already exists in database, id={:d}".format(str(hole), hole_id))

            # Build tee set update query
            query = hole._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add/update tee set data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve tee set id for this tee set (if necessary)
        hole_id = hole.hole_id
        if hole_id is None:
            hole_id = self.get_hole_id(hole.tee_set_id, hole.number, verbose=verbose)
        if verbose:
            print("Added/updated hole '{:s}' (id={:d}) in holes table".format(str(hole), hole_id))

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
            Default: False
        
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

    def get_flight_id(self, name, year, verbose=False):
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
        Adds/updates golf flight data in database, populating 'flights' table.

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

    def get_player_by_name(self, first_name, last_name, verbose=False):
        r"""
        Fetches golf player data for the player matching the given parameters.

        If a matching player cannot be found in the database, returns None.

        Parameters
        ----------
        first_name : string
            player first name
        last_name : int
            player last name
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        player : GolfPlayer
            golf player data
            if no match is found, returns None

        """
        # Build query
        query = "SELECT classification, email, phone, location, employee_id FROM players WHERE first_name='{:s}' AND last_name='{:s}';".format(first_name, last_name)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched golf player or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        
        player = GolfPlayer(first_name, last_name, result[0], result[1])
        player.phone = result[2]
        player.location = result[3]
        player.employee_id = result[4]
        return player

    def get_player_by_id(self, player_id, verbose=False):
        r"""
        Fetches golf player data using the given player identifier.

        If a matching player cannot be found in the database, returns None.

        Parameters
        ----------
        player_id : int
            player identifier
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        player : GolfPlayer
            golf player data
            if no match is found, returns None

        """
        # Build query
        query = "SELECT first_name, last_name, classification, email, phone, location, employee_id FROM players WHERE id={:d};".format(player_id)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched golf player or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        
        player = GolfPlayer(result[0], result[1], result[2], result[3])
        player.phone = result[4]
        player.location = result[5]
        player.employee_id = result[6]
        return player

    def get_player_id(self, first_name, last_name, verbose=False):
        r"""
        Fetches player identifier for the player matching the given parameters.

        If a matching player cannot be found in the database, returns None.

        Parameters
        ----------
        first_name : string
            player first name
        last_name : string
            player last name
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        player_id : int
            golf player identifier from database
            if no match is found, returns None

        """
        # Build query
        query = "SELECT id FROM players WHERE first_name='{:s}' AND last_name='{:s}';".format(first_name, last_name)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched player id or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_player(self, player: GolfPlayer, update=False, verbose=False):
        r"""
        Adds/updates golf player data in database, populating 'players' table.

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
        player_id = self.get_player_id(player.first_name, player.last_name, verbose=verbose)
        if player_id is None:
            # Build flight insert query
            query = player._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Player '{:s}' already exists in database, id={:d}".format(str(player), player_id))

            # Build flight update query
            query = player._create_database_update_query(player_id)

        if verbose:
            print("Executing query: {:s}".format(query))
        
        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()
        
        if verbose:
            print("Added/updated player '{:s}' to players table".format(str(player)))

    def get_team(self, flight_id: int, number: int, verbose=False):
        r"""
        Fetches golf league team information matching the given parameters.

        If a matching team cannot be found in the database, returns None.

        Parameters
        ----------
        flight_id : int
            flight identifier in database
        number : int
            team number
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        team : GolfTeam
            golf team data
            if no match is found, returns None

        """
        # Build query
        query = "SELECT name FROM teams WHERE flight_id={:d} AND number={:d};".format(flight_id, number)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched team or None (if not found)
        if len(data) == 0:
            return None
        result = data[0]
        
        team = GolfTeam(flight, number)
        team.name = result[0]
        return team
