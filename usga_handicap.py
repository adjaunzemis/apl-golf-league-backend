r"""
USGA handicap calculation

Authors
-------
Andris Jaunzemis

"""

def compute_adjusted_gross_score(par, handicap, score, index=None):
    r"""
    Computes adjusted gross score on a hole for handicapping purposes.

    Parameters
    ----------
    par : int
        hole par
    handicap : int
        hole handicap
    score : int
        gross score recorded for this hole
    index : int, optional
        player course handicap index
        Default: None (handicap index not established)
    
    Returns
    -------
    score_adjusted : int
        adjusted gross score for this hole
    
    References
    ----------
    USGA Rule 3.1

    """
    return min(score, compute_maximum_score(par, handicap, index=index))

def compute_maximum_score(par, handicap, index=None):
    r"""
    Computes maximum score on a hole for handicapping purposes.

    If handicap index has been established, maximum is net double bogey.
    If handicap index has not been established, maximum is five over par.

    Parameters
    ----------
    par : int
        hole par
    handicap : int
        hole handicap
    index : int, optional
        player course handicap index
        Default: None (handicap index not estalished)
    
    Returns
    -------
    max_score : int
        maximum score allowed for handicap purposes
    
    References
    ----------
    USGA Rule 3.1

    """
    if index is None:
        return par + 5
    handicap_strokes = compute_handicap_strokes(handicap, index)
    if handicap_strokes > 3:
        return par + 5
    return par + 2 + handicap_strokes

def compute_handicap_strokes(handicap, index):
    r"""
    Computes handicap stokes a player recieves on a hole.

    Parameters
    ----------
    handicap : int
        hole handicap
    index : int
        player course handicap index
    
    Returns
    -------
    strokes : int
        handicap strokes received
    
    References
    ----------
    USGA Rule 3.1
    
    """
    strokes = 0
    if handicap > 0:
        while index > 18:
            strokes += 1
            index -= 18
        if handicap <= index:
            strokes += 1
    else:
        if (18 - handicap) < abs(index):
            strokes -= 1
    return strokes

def compute_course_handicap(par, rating, slope, index):
    r"""
    Computes course handicap.

    Parameters
    ----------
    par : int
        course par
    rating : float
        course rating
    slope : float
        course slope rating
    index : float   
        player handicap index

    Returns
    -------
    handicap : float
        player course handicap index

    References
    ----------
    USGA Rule 6.1

    """
    return index * (slope / 113) + (rating - par)

def compute_score_differential(rating, slope, score, conditions_adjustment=0.0):
    r"""
    Computes score differential.

    Parameters
    ----------
    rating : float
        course rating
    slope : float
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
    return int(score_diff * 10) / 10

def round_toward_zero(value, digits=0):
    r"""
    Rounds given value toward zero.

    Parameters
    ----------
    value : float
        value to round
    digits : int
        number of decimal point digits to preserve
        Default: 0 (round to nearest integer)

    Returns
    -------
    result : float
        rounded value

    """
    scale = pow(10.0, digits)
    if ((((scale * value) % 10) / scale) <= 0.5):
        return int(value * scale) / scale
    else:
        return int(value * scale + 1) / scale
