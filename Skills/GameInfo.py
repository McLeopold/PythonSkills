from Rating import Rating

class GameInfoError(Exception):
    pass

class GameInfo():
    '''
    Parameters about the game for calculating theTrueSkill.
    '''

    DEFAULT_INITIAL_MEAN = 25.0
    DEFAULT_INITIAL_STANDARD_DEVIATION = DEFAULT_INITIAL_MEAN / 3
    DEFAULT_BETA = DEFAULT_INITIAL_MEAN / 6
    DEFAULT_DYNAMICS_FACTOR = DEFAULT_INITIAL_MEAN / 300
    DEFAULT_DRAW_PROBABILITY = 0.10
    DEFAULT_CONSERVATIVE_STANDARD_DEVIATION_MULTIPLIER = 3.0

    def __init__(self, initial_mean=DEFAULT_INITIAL_MEAN,
                       stdev=DEFAULT_INITIAL_STANDARD_DEVIATION,
                       beta=DEFAULT_BETA,
                       dynamics_factor=DEFAULT_DYNAMICS_FACTOR,
                       draw_probability=DEFAULT_DRAW_PROBABILITY,
                       conservative_stdev_multiplier=DEFAULT_CONSERVATIVE_STANDARD_DEVIATION_MULTIPLIER):

        try:
            self.initial_mean = float(initial_mean)
            self.initial_stdev = float(stdev)
            self.beta = float(beta)
            self.dynamics_factor = float(dynamics_factor)
            self.draw_probability = float(draw_probability)
            self.conservative_stdev_multiplier = float(conservative_stdev_multiplier)
        except ValueError:
            raise GameInfoError("GameInfo arguments must be numeric")

    def default_rating(self):
        return Rating(self.initial_mean, self.initial_stdev)
