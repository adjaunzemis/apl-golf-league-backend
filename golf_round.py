r"""
Golf round data model

Authors
-------
Andris Jaunzemis

"""

from datetime import datetime

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
        raise NotImplementedError("TODO: Implement _create_database_insert_query()")

    def _create_database_update_query(self):
        raise NotImplementedError("TODO: Implement _create_database_update_query")

    def add_result(self, result: GolfHoleResult)
        r"""
        Add a hole result to this round.

        Parameters
        ----------
        result : GolfHoleResult
            result to add
        
        """
        raise NotImplementedError("TODO: Implement add_result()")
        