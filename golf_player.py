r"""
Golf player data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime
from golf_player_contact import GolfPlayerContact

class GolfPlayer(object):
    r"""
    Container for golf player information

    """

    def __init__(self, last_name: str, first_name: str, affiliation: str, middle_name: str = None, player_id: int = None, date_created: datetime = None, date_updated: datetime = None):
        self.last_name = last_name
        self.first_name = first_name
        self.affiliation = affiliation
        self.middle_name = middle_name
        self.player_id = player_id
        self.date_created = date_created
        self.date_updated = date_updated
        self.contacts = []

    def __str__(self):
        r"""
        Customizes string representation for this player.
        
        Returns
        -------
        s : string
            string representation of player

        """
        if self.middle_name is not None:
            return "{:s}, {:s}.{:s}.".format(self.last_name, self.first_name[0], self.middle_name[0])
        return "{:s}, {:s}.".format(self.last_name, self.first_name[0])

    @classmethod
    def from_dict(cls, player_data):
        r"""
        Initializes player from dictionary representation.

        Parameters
        ----------
        player_data : dict
            dictionary of player data

        Returns
        -------
        player : GolfPlayer
            player parsed from given data
        
        """
        player = cls(
            player_id = player_data['player_id'] if player_data['player_id'] != -1 else None,
            last_name = player_data['last_name'],
            first_name = player_data['first_name'],
            affiliation = player_data['affiliation']
        )

        for key in ['middle_name']:
            if key in player_data:
                setattr(player, key, player_data[key])

        for contact_data in player_data['contacts']:
            player.add_contact(GolfPlayerContact.from_dict(contact_data))

        return player

    def as_dict(self):
        r"""
        Creates dictionary representation of this player.

        Returns
        -------
        player_dict : dict
            dictionary representation of player data

        """
        player_dict = {
            'player_id': self.player_id,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'affiliation': self.affiliation,
            'contacts': [contact.as_dict() for contact in self.contacts]
        }

        if self.middle_name is not None:
            player_dict['middle_name'] = self.middle_name
        if self.date_created is not None:
            player_dict['date_created'] = self.date_created
        if self.date_updated is not None:
            player_dict['date_updated'] = self.date_updated
        
        return player_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this player into database.

        Returns
        -------
        query : string
            database insert query for player

        """
        # Add required fields
        fields = "last_name, first_name, affiliation"
        values = "'{:s}', '{:s}', '{:s}'".format(self.last_name, self.first_name, self.affiliation)

        # Add optional fields if defined
        if self.middle_name is not None:
            fields += ", middle_name"
            values += ", '{:s}'".format(self.middle_name)
        
        # Construct query
        return "INSERT INTO players ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this player in database.

        Returns
        -------
        query :string
            database update query for player

        """
        # Add required fields
        fieldValues = "last_name = '{:s}', first_name = '{:s}', affiliation = '{:s}'".format(
            self.last_name, self.first_name, self.affiliation
        )

        # Add optional fields if defined
        if self.middle_name is not None:
            fieldValues += ", middle_name = '{:s}'".format(self.middle_name)

        # Construct conditions
        if self.player_id is None:
            raise ValueError("Cannot update player data in database without player_id")
        conditions = "player_id = {:d}".format(self.player_id)

        # Construct query
        return "UPDATE players SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_contact(self, contact: GolfPlayerContact):
        r"""
        Add contact information to this player.
        
        Parameters
        ----------
        contact : GolfPlayerContact
            contact info to add
        
        Raises
        ------
        ValueError :
            if player identifier for given contact does not mat this player identifier

        """
        if contact.player_id != self.player_id:
            raise ValueError("Cannot add contact with player_id={:d} to player with id={:d}".format(contact.player_id, self.player_id))
        self.contacts.append(contact)
    