r"""
Golf player contact information

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime

class GolfPlayerContact(object):
    r"""
    Container for player contact information.

    """

    def __init__(self, type: str, contact: str, contact_id: int = None, player_id: int = None, date_updated: datetime = None):
        self.type = type
        self.contact = contact
        self.contact_id = contact_id
        self.player_id = player_id
        self.date_updated = date_updated

    def __str__(self):
        r"""
        Customizes string representation for this contact.

        Returns
        -------
        s : string
            string representation of contact

        """
        return "{:s}: {:s}".format(self.type, self.contact)

    @classmethod
    def from_dict(cls, contact_data):
        r"""
        Initializes contact from dictionary representation.

        Parameters
        ----------
        contact_data : dict
            dictionary of contact data

        Returns
        -------
        contact : GolfPlayerContact
            contact information parsed from given data

        """
        return cls(
            contact_id = contact_data['contact_id'] if contact_data['contact_id'] != -1 else None,
            player_id = contact_data['player_id'] if contact_data['player_id'] != -1 else None,
            type = contact_data['type'],
            contact = contact_data['contact']
        )

    def as_dict(self):
        r"""
        Creates dictionary representation of this contact.

        Returns
        -------
        contact_dict : dict
            dictionary representation of contact information

        """
        contact_dict = {
            'contact_id': self.contact_id,
            'player_id': self.player_id,
            'type': self.type,
            'contact': self.contact
        }

        if self.date_updated is not None:
            contact_dict['date_updated'] = self.date_updated.strftime("%Y-%m-%d")

        return contact_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this contact into database.

        Returns
        -------
        query : string
            database insert query for contact information
            
        """
        # Add required fields
        fields = "player_id, type, contact"
        values = "{:d}, '{:s}', '{:s}'".format(self.player_id, self.type, self.contact)

        # Construct query
        return "INSERT INTO player_contacts ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this contact in database.

        Returns
        -------
        query : string
            database update query for contact information

        """
        # Add required fields
        fieldValues = "contact = '{:s}'".format(self.contact)
        
        # Construct conditions
        if self.player_id is None:
            raise ValueError("Cannot update contact information in database without player_id")
        conditions = "player_id = {:d} AND type = '{:s}'".format(self.player_id, self.type)

        # Construct query
        return "UPDATE player_contacts SET {:s} WHERE {:s};".format(fieldValues, conditions)
