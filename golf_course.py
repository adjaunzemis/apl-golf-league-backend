r"""
Golf course data model

Authors
-------
Andris Jaunzemis

"""

from golf_track import GolfTrack

class GolfCourse(object):
    r"""
    Container for 9-hole track on a golf course.

    """

    def __init__(self, id: int, name: str, abbreviation: str):
        self.id = id
        self.name = name
        self.abbreviation = abbreviation
        self.address: str = None
        self.city: str = None
        self.state: str = None
        self.zip_code: int = None
        self.phone: str = None
        self.website: str = None
        self.date_updated = None
        self.tracks = []

    def __str__(self):
        r"""
        Customizes string representation for this course.

        Returns
        -------
        s : string
            string representation of course

        """
        return "{:s}".format(self.name)

    @classmethod
    def from_dict(cls, course_data):
        r"""
        Initializes course from dictionary representation.

        Parameters
        ----------
        course_data : dict
            dictionary of course data

        Returns
        -------
        course : GolfCourse
            course parsed from given data

        """
        course = cls(
            course_data['id'],
            course_data['name'],
            course_data['abbreviation']
        )

        for key in ['address', 'city', 'state', 'zip_code', 'phone', 'website']:
            if key in course_data:
                setattr(course, key, course_data[key])

        for track_data in course_data['tracks']:
            course.add_track(GolfTrack.from_dict(track_data))

        return course
    
    def as_dict(self):
        r"""
        Creates dictionary representation of this course.

        Returns
        -------
        course_dict : dict
            dictionary representation of course data

        """
        course_dict = {
            'id': self.id,
            'name': self.name,
            'abbreviation': self.abbreviation,
            'tracks': [track.as_dict() for track in self.tracks]
        }

        if self.address is not None:
            course_dict['address'] = self.address
        if self.city is not None:
            course_dict['city'] = self.city
        if self.state is not None:
            course_dict['state'] = self.state
        if self.zip_code is not None:
            course_dict['zipCode'] = self.zip_code
        if self.phone is not None:
            course_dict['phone'] = self.phone
        if self.website is not None:
            course_dict['website'] = self.website
        if self.date_updated is not None:
            course_dict['dateUpdated'] = self.date_updated.strftime("%Y-%m-%d")

        return course_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this course into database.

        Returns
        -------
        query : string
            database insert query for course

        """
        # Add required fields
        fields = "name, abbreviation"
        values = "'{:s}', '{:s}'".format(self.name, self.abbreviation)

        # Add optional fields if defined
        if self.address is not None:
            fields += ", address"
            values += ", '{:s}'".format(self.address)
        if self.city is not None:
            fields += ", city"
            values += ", '{:s}'".format(self.city)
        if self.state is not None:
            fields += ", state"
            values += ", '{:s}'".format(self.state)
        if self.zip_code is not None:
            fields += ", zip_code"
            values += ", {:d}".format(self.zip_code)
        if self.phone is not None:
            fields += ", phone"
            values += ", '{:s}'".format(self.phone)
        if self.website is not None:
            fields += ", website"
            values += ", '{:s}'".format(self.website)

        # Construct query
        return "INSERT INTO courses ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this course in database.

        Returns
        -------
        query : string
            database update query for course

        """
        # Add required fields
        fieldValues = "name = '{:s}', abbreviation = '{:s}'".format(self.name, self.abbreviation)

        # Add optional fields if defined
        if self.address is not None:
            fieldValues += ", address = '{:s}'".format(self.address)
        if self.city is not None:
            fieldValues += ", city = '{:s}'".format(self.city)
        if self.state is not None:
            fieldValues += ", state = '{:s}'".format(self.state)
        if self.zip_code is not None:
            fieldValues += ", zip_code = '{:d}'".format(self.zip_code)
        if self.phone is not None:
            fieldValues += ", phone = '{:s}'".format(self.phone)
        if self.website is not None:
            fieldValues += ", website = '{:s}'".format(self.website)

        # Construct conditions
        if self.id is not None:
            conditions = "id = {:d}".format(self.id)
        else:
            conditions = "name = '{:s}'".format(self.name)

        # Construct query
        return "UPDATE courses SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_track(self, track: GolfTrack):
        r"""
        Add a track to this golf course.

        Parameters
        ----------
        track : GolfTrack
            track to add

        Raises
        ------
        ValueError :
            if course identifier for given track does not match this course identifier
            if this course already contains a track with the given name
        
        """
        if track.course_id != self.id:
            raise ValueError("Cannot add track with course id={:d} to course with id={:d}".format(track.course_id, self.id))
        if track.name in [t.name for t in self.tracks]:
            raise ValueError("Course '{:s}' (id={:d}) already contains a track with name='{:s}'".format(self.name, self.id, track.name))
        self.tracks.append(track)
