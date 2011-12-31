class PairwiseComparison():
    '''
    Represents a comparison between two players.
    '''

    WIN = 1
    DRAW = 0
    LOSE = -1

    @staticmethod
    def get_rank_from_comparison(comparison):
        if comparison == PairwiseComparison.WIN:
            return (1, 2)
        elif comparison == PairwiseComparison.LOSE:
            return (2, 1)
        else:
            return (1, 1)
