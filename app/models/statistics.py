from sqlmodel import SQLModel

class GolferStatistics(SQLModel):
    num_rounds: int = 0
    num_holes: int = 0
    avg_gross_score: float = 0
    avg_net_score: float = 0
    num_aces: int = 0
    num_albatrosses: int = 0
    num_eagles: int = 0
    num_birdies: int = 0
    num_pars: int = 0
    num_bogeys: int = 0
    num_double_bogeys: int = 0
    num_others: int = 0
