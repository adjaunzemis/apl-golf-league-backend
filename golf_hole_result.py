r"""
Golf hole result data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime
from dataclasses import dataclass

@dataclass
class GolfHoleResult(object):
    r"""
    Container class for results from a hole in a golf round.
    
    """

    round_id: int
    hole_id: int
    strokes: int
    hole_result_id: int = None
    date_updated: int = None
    
    def __str__(self):
        r"""
        Customizes string representation for this hole result.
        
        Returns
        -------
        s : string
            string representation of this hole result
            
        """
        return "Hole Result" # TODO: Add details

    @classmethod
    def from_dict(cls, hole_result_data):
        r"""
        Initializes hole result from dictionary representation.
        
        Parameters
        ----------
        hole_result_data : dict
            dictionary of hole result data
            
        Returns
        -------
        hole_result : GolfHoleResult
            hole result parsed from given data

        """
        hole_result = cls(
            hole_result_id = hole_result_data['hole_result_id'] if hole_result_data['hole_result_id'] != -1 else None,
            round_id = hole_result_data['round_id'] if hole_result_data['round_id'] != -1 else None,
            hole_id = hole_result_data['hole_id'] if hole_result_data['hole_id'] != -1 else None,
            strokes = hole_result_data['strokes']
        )

        return hole_result

    def as_dict(self):
        r"""
        Creates dictionary representation of this hole result.
        
        Returns
        -------
        hole_result_dict : dict
            dictionary representation of hole result information
        
        """
        hole_result_dict = {
            'hole_result_id': self.hole_result_id,
            'round_id': self.round_id,
            'hole_id': self.hole_id,
            'strokes': self.strokes
        }

        if self.date_updated is not None:
            hole_result_dict['date_updated'] = self.date_updated.strftime('%Y-%m-%d')

        return hole_result_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this hole result into database.

        Returns
        -------
        query : string
            database insert query for hole result

        """
        # Add required fields
        fields = "hole_result_id, round_id, hole_id, strokes"
        values = "{:d}, {:d}, {:d}, {:d}".format(self.hole_result_id, self.round_id, self.hole_id, self.strokes)
    
        # Construct query
        return "INSERT INTO hole_results ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this hole result in database.
        
        Returns
        -------
        query : string
            database update query for hole result
        
        """
        # Add required fields
        fieldValues = "round_id = {:d}, hole_id = {:d}, strokes = {:d}".format(self.round_id, self.hole_id, self.strokes)

        # Construct conditions
        if self.hole_result_id is None:
            raise ValueError("Cannot update hole result in database without hole_result_id")
        conditions = "hole_result_id = {:d}".format(self.hole_result_id)

        # Construct query
        return "UPDATE hole_results SET {:s} WHERE {:s};".format(fieldValues, conditions)
