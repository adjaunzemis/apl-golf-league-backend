from abc import ABC, abstractmethod

class HandicapSystem(ABC):

    @staticmethod
    @abstractmethod
    def compute_adjusted_gross_score(par: int, stroke_index: int, score: int, course_handicap: int = None) -> int:
        r"""
        Computes adjusted gross score on a hole for handicapping purposes.

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
        ...
    
    @staticmethod
    @abstractmethod
    def compute_maximum_score(par: int, stroke_index: int, course_handicap: int = None) -> int:
        r"""
        Computes maximum score on a hole for handicapping purposes.

        If handicap index has been established, maximum is net double bogey.
        If handicap index has not been established, maximum is five over par.

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
        ...

    @staticmethod
    @abstractmethod
    def compute_handicap_strokes(stroke_index: int, course_handicap: int) -> int:
        r"""
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
        ...

    @staticmethod
    @abstractmethod
    def compute_course_handicap(par: int, rating: float, slope: int, handicap_index: float) -> int:
        r"""
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
        ...
    
    @staticmethod
    @abstractmethod
    def compute_score_differential(rating: float, slope: int, score: int, playing_conditions_correction: float) -> int:
        r"""
        Computes score differential.

        Parameters
        ----------
        rating : float
            course rating
        slope : int
            course slope rating
        score : int
            adjusted gross score
        playing_conditions_correction : float, optional
            playing conditions correction adjustment
            Default: 0.0

        Returns
        -------
        score_diff : float
            score differential, rounded nearest tenth and toward zero

        """
        ...
