r"""
USGA handicap calculation

Authors
-------
Andris Jaunzemis

"""

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
    
    References
    ----------
    USGA Rule 3.1

    """
    return min(score, compute_maximum_score(par, stroke_index, course_handicap=course_handicap))

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
    
    References
    ----------
    USGA Rule 3.1

    """
    if course_handicap is None:
        return par + 5
    handicap_strokes = compute_handicap_strokes(stroke_index, course_handicap)
    if handicap_strokes > 3:
        return par + 5
    return par + 2 + handicap_strokes

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
    
    References
    ----------
    USGA Rule 3.1
    
    """
    strokes = 0
    if stroke_index > 0:
        while course_handicap > 18:
            strokes += 1
            course_handicap -= 18
        if stroke_index <= course_handicap:
            strokes += 1
    else:
        if (18 - stroke_index) < abs(course_handicap):
            strokes -= 1
    return strokes

def compute_course_handicap(par: int, rating: float, slope: int, handicap_index: float) -> float:
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

    References
    ----------
    USGA Rule 6.1

    """
    return handicap_index * (slope / 113) + (rating - par)

def compute_score_differential(rating: float, slope: int, score: int, conditions_adjustment: float = 0.0):
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
    conditions_adjustment : float, optional
        playing conditions calculation adjustment
        Default: 0.0

    Returns
    -------
    score_diff : float
        score differential, rounded nearest tenth and toward zero
    
    References
    ----------
    USGA Rule 5.1

    """
    score_diff = (113 / slope) * (score - rating - conditions_adjustment)
    return round(score_diff * 10, 1)
