r"""
Golf round data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime

from golf_hole_result import GolfHoleResult

class GolfRound(object):
    r"""
    Container class for a golf round.

    """

    def __init__(self, date_played: datetime, player_handicap_index: int, player_playing_handicap: float, tee_set_id: int, player_id: int, round_id: int = None, date_updated: datetime = None):
        self.date_played = date_played
        self.player_handicap_index = player_handicap_index
        self.player_playing_handicap = player_playing_handicap
        self.tee_set_id = tee_set_id
        self.player_id = player_id
        self.round_id = round_id
        self.date_updated = date_updated
        self.results = []

    def __str__(self):
        r"""
        Customizes string representation for this round.
        
        Returns
        -------
        s : string
            string representation of round

        """
        return "Round" # TODO: Add details

    @classmethod
    def from_dict(cls, round_data):
        r"""
        Initializes round from dictionary representation.
        
        Parameters
        ----------
        round_data : dict
            dictionary of round data
        
        Returns
        -------
        round : GolfRound
            round parsed from given data

        """
        round = cls(
            round_id = round_data['round_id'] if round_data['round_id'] != -1 else None,
            tee_set_id = round_data['round_id'] if round_data['round_id'] != -1 else None,
            player_id = round_data['player_id'] if round_data['player_id'] != -1 else None,
            date_played = round_data['date_played'],
            player_handicap_index = round_data['player_handicap_index'],
            player_playing_handicap = round_data['player_playing_handicap']
        )

        for result_data in round_data['results']:
            round.add_hole_result(GolfHoleResult.from_dict(result_data))

        return round

    def as_dict(self):
        r"""
        Creates dictionary representation of this round.

        Returns
        -------
        round_dict : dict
            dictionary representation of round data

        """
        round_dict = {
            'round_id': self.round_id,
            'tee_set_id': self.tee_set_id,
            'player_id': self.player_id,
            'date_played': self.date_played.strftime("%Y-%m-%d"),
            'player_handicap_index': self.player_handicap_index,
            'player_playing_handicap': self.player_playing_handicap,
            'results': [result.as_dict() for result in self.results]
        }

        if self.date_updated is not None:
            round_dict['date_updated'] = self.date_updated.strftime("%Y-%m-%d")

        return round_dict

    def _create_database_insert_query(self):
        r"""
        Creates query for inserting this round into database.
        
        Returns
        -------
        query : string
            database insert query for round
            
        """
        # Add required fields
        fields = "round_id, tee_set_id, player_id, date_played, player_handicap_index, player_playing_handicap, gross_score, adjusted_gross_score, net_score, score_differential"
        values = "{:d}, {:d}, {:d}, '{:s}', {:f}, {:f}, {:d}, {:d}, {:d}, {:f}".format(self.round_id, self.tee_set_id, self.player_id, self.date_played, self.player_handicap_index, self.player_playing_handicap, self.gross_score, self.adjusted_gross_score, self.net_score, self.score_differential)

        # Construct query
        return "INSERT INTO rounds ({:s}) VALUES ({:s});".format(fields, values)

    def _create_database_update_query(self):
        r"""
        Creates query for updating this round in database.
        
        Returns
        -------
        query : string
            database update query for round

        """
        # Add required fields
        fieldValues = "tee_set_id = {:d}, player_id = {:d}, date_played = '{:s}', player_handicap_index = {:f}, player_playing_handicap = {:f}, gross_score = {:d}, adjusted_gross_score = {:d}, net_score = {:d}, score_differential = {:f}".format(
            self.tee_set_id, self.player_id, self.date_played, self.player_handicap_index, self.player_playing_handicap, self.gross_score, self.adjusted_gross_score, self.net_score, self.score_differential
        )

        # Construct conditions
        if self.round_id is None:
            raise ValueError("Cannot update round data in database without round_id")
        conditions = "round_id = {:d}".format(self.round_id)

        # Construct query
        return "UPDATE rounds SET {:s} WHERE {:s};".format(fieldValues, conditions)

    def add_result(self, hole_result: GolfHoleResult):
        r"""
        Add a hole result to this round.

        Parameters
        ----------
        hole_result : GolfHoleResult
            hole result to add
        
        """
        if hole_result.round_id != self.round_id:
            raise ValueError("Cannot add hole result with round_id={:d} to round with id={:d}".format(hole_result.round_id, self.round_id))
        self.hole_results.append(hole_result)
        