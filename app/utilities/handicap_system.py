from typing import List
from abc import ABC, abstractmethod, abstractproperty

class HandicapSystem(ABC):
    """
    Defines functionality a golf handicap system must support.
    """

    @abstractmethod
    def compute_hole_adjusted_gross_score(self, par: int, stroke_index: int, score: int, course_handicap: int = None) -> int:
        """
        Computes adjusted gross score on a hole for handicapping purposes.

        Adjusted gross score accounts for maximum allowed strokes per hole
        based on player handicap and hole stroke index.

        See also: Equitable Stroke Control

        Parameters
        ----------
        par : int
            hole par
        stroke_index : int
            hole stroke index
        score : int
            gross score recorded for this hole
        course_handicap : int, optional
            player course handicap
            Default: None (player handicap index not established)
        
        Returns
        -------
        score_adjusted : int
            adjusted gross score for this hole

        """
    
    @abstractmethod
    def compute_hole_maximum_score(self, par: int, stroke_index: int, course_handicap: int = None) -> int:
        """
        Computes maximum score on a hole for handicapping purposes.

        Parameters
        ----------
        par : int
            hole par
        stroke_index : int
            hole stroke index
        course_handicap : int, optional
            player course handicap
            Default: None (player handicap index not estalished)
        
        Returns
        -------
        max_score : int
            maximum score allowed for handicap purposes

        """

    @abstractmethod
    def compute_hole_handicap_strokes(self, stroke_index: int, course_handicap: int) -> int:
        """
        Computes handicap stokes a player recieves on a hole.

        Parameters
        ----------
        stroke_index : int
            hole stroke index
        course_handicap : int
            player course handicap
        
        Returns
        -------
        strokes : int
            handicap strokes received
        
        """

    @abstractmethod
    def compute_course_handicap(self, par: int, rating: float, slope: int, handicap_index: float) -> int:
        """
        Computes course handicap.

        Parameters
        ----------
        par : int
            course par
        rating : float
            course rating
        slope : int
            course slope rating
        handicap_index : float   
            player handicap index

        Returns
        -------
        course_handicap : float
            player course handicap index

        """
    
    @abstractmethod
    def compute_score_differential(self, rating: float, slope: int, score: int, playing_conditions_correction: float) -> int:
        """
        Computes score differential for a round using course rating and slope.

        Parameters
        ----------
        rating : float
            course rating
        slope : int
            course slope rating
        score : int
            adjusted gross score for the round
        playing_conditions_correction : float, optional
            playing conditions correction adjustment
            Default: 0.0

        Returns
        -------
        score_diff : float
            score differential

        """

    @abstractmethod
    def compute_handicap_index(self, record: List[float]) -> float:
        """
        Computes handicap index for a given scoring record.

        Parameters
        ----------
        record: list of floats
            score differentials in scoring record

        Returns
        -------
        handicap_index : float
            handicap index
        """

    @property
    @abstractmethod
    def maximum_handicap_index(self) -> float:
        """
        Defines maximum handicap index that can be issued to a player.

        Returns
        -------
        max_handicap_index : float
            maximum allowed handicap index
        
        """
