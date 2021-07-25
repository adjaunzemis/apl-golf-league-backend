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
from golf_player import GolfPlayer
from golf_player_contact import GolfPlayerContact

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
                course_id = course_data[0],
                name = course_data[1],
                address = course_data[2],
                city = course_data[3],
                state = course_data[4],
                zip_code = course_data[5],
                phone = course_data[6],
                website = course_data[7],
                date_updated = course_data[8]
            )
            
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
        query = "SELECT track_id, course_id, name FROM tracks"
        if any(val is not None for val in (track_id, course_id, name)):
            query += " WHERE"
            condition_count = 0
            if track_id is not None:
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
                track_id = track_data[0],
                course_id = track_data[1],
                name = track_data[2]
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
                query += " tee_set_id = {:d}".format(tee_set_id)
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
                tee_set_id = tee_set_data[0],
                track_id = tee_set_data[1],
                name = tee_set_data[2],
                gender = tee_set_data[3],
                rating = tee_set_data[4],
                slope = tee_set_data[5],
                color = tee_set_data[6]
            )
            
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
            if hole_id is not None:
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
                hole_id = hole_data[0],
                tee_set_id = hole_data[1],
                number = hole_data[2],
                par = hole_data[3],
                handicap = hole_data[4],
                yardage = hole_data[5]
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
        query = "SELECT last_name, first_name, middle_name, affiliation FROM players WHERE player_id={:d};".format(player_id)
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
        
        player = GolfPlayer(
            last_name = result[0],
            first_name = result[1],
            middle_name = result[2],
            affiliation = result[3]
        )
        return player

    def get_player_id(self, last_name, first_name, verbose=False):
        r"""
        Fetches player identifier for the player matching the given parameters.

        If a matching player cannot be found in the database, returns None.

        Parameters
        ----------
        last_name : string
            player last name
        first_name : string
            player first name
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
        query = "SELECT player_id FROM players WHERE last_name='{:s}' AND first_name='{:s}';".format(last_name, first_name)
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched player id or None (if not found)
        # TODO: Handle multiple results for same name?
        if len(data) == 0:
            return None
        result = data[0]
        return result[0]

    def put_player(self, player: GolfPlayer, update=False, verbose=False):
        r"""
        Adds/updates golf player data in database, populating 'players' table.

        Also calls 'put_player_contact' for each contact in this player.

        Parameters
        ----------
        player : GolfPlayer
            golf player data to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        # Check if player already exists in database
        player_id = self.get_player_id(player.last_name, player.first_name, verbose=verbose)
        if player_id is None:
            # Build player insert query
            query = player._create_database_insert_query()
        else:
            # Set local id (if necessary)
            if player.player_id is None:
                player.player_id = player_id
            else:
                if player_id != player.player_id:
                    raise ValueError("Player '{:s}' already exists in database with id={:d}, but has local id={:d}".format(str(player), player.player_id, player_id))

            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Player '{:s}' already exists in database, id={:d}".format(str(player), player_id))

            # Build player update query
            query = player._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))
        
        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve player id for this player (if necessary)
        player_id = player.player_id
        if player_id is None:
            player_id = self.get_player_id(last_name=player.last_name, first_name=player.first_name, verbose=verbose)
        if verbose:
            print("Added/updated player '{:s}' (id={:d}) in players table".format(str(player), player_id))

        # Build and execute queries to add player contacts to database
        for contact in player.contacts:
            if contact.player_id is None:
                contact.player_id = player_id
            self.put_player_contact(contact, update=update, verbose=verbose)

    def get_player_contacts(self, player_id: int, verbose=False):
        r"""
        Fetches contact information for a specific player.

        Parameters
        ----------
        player_id : int
            player identifier in database
        verbose : boolean, optional
            if true, prints details to console
            Default: False
        
        Returns
        -------
        contacts : list of GolfPlayerContacts
            contact information

        """
        # Build query
        query = "SELECT contact_id, type, contact FROM player_contacts WHERE player_id = {:d};".format(player_id)

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched contact information
        contacts = []
        for contact_data in data:
            contact = GolfPlayerContact(
                contact_id = contact_data[0],
                player_id = player_id,
                type = contact_data[1],
                contact = contact_data[2]
            )

            # Append contact to contacts list
            contacts.append(contact)

        # Return contacts
        return contacts

    def get_player_contact_by_type(self, player_id: int, type: str, verbose):
        r"""
        Fetches player contact information of a specific type for a specific player.
        
        If no matching contact information is found, returns None.

        Parameters
        ----------
        player_id : int
            player identifier
        type : str
            contact type
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        Returns
        -------
        contact : GolfPlayerContact
            player contact information
            if no match is found, returns None

        """
        # Build query
        query = "SELECT contact_id, contact FROM player_contacts WHERE player_id = {:d} AND type = '{:s}';".format(player_id, type)
        
        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query
        cursor = self._connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        # Return matched contact information
        if len(data) == 0:
            return None
        
        # TODO: Handle multiple returns?
        contact_data = data[0]
        return GolfPlayerContact(
            contact_id = contact_data[0],
            player_id = player_id,
            type = type,
            contact = contact_data[1]
        )

    def put_player_contact(self, contact: GolfPlayerContact, update=False, verbose=False):
        r"""
        Adds/updates golf player contact information in database, populating 'player_contacts' table.

        Parameters
        ----------
        contact : GolfContact
            golf player contact information to add
        update : boolean, optional
            if true, allows updating of existing database entries
            Default: False
        verbose : boolean, optional
            if true, prints details to console
            Default: False

        """
        # Check input data integrity before adding to database.
        if not isinstance(contact, GolfPlayerContact):
            raise TypeError("Input must be a GolfPlayerContact")

        # Check if contact already exists in database
        contact_db = self.get_player_contact_by_type(contact.player_id, contact.type, verbose=verbose)
        if contact_db is None:
            # Build tee set insert query
            query = contact._create_database_insert_query()
        else:
            # If existing entry updates are not allowed, raise exception
            if not update:
                raise ValueError("Contact '{:s}' already exists in database, id={:d}".format(str(contact), contact_db.contact_id))

            # Build tee set update query
            query = contact._create_database_update_query()

        if verbose:
            print("Executing query: {:s}".format(query))

        # Execute query to add/update tee set data
        cursor = self._connection.cursor()
        cursor.execute(query)
        self._connection.commit()
        cursor.close()

        # Retrieve tee set id for this tee set (if necessary)
        if contact.contact_id is None:
            contact_db = self.get_player_contact_by_type(contact.player_id, contact.type, verbose=verbose)
            contact.contact_id = contact_db.contact_id
        if verbose:
            print("Added/updated contact '{:s}' (id={:d}) in player_contacts table".format(str(contact), contact.contact_id))
