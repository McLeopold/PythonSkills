from collections import Sequence

from skills import (
    Calculator,
    Match,
    Team,
    Rating,
    RatingFactory,
    WIN,
    LOSE,
    DRAW,
    )

from skills.numerics import Range

class EloGameInfo(object):
    '''Parameters about the game used for calculating new skills'''

    DEFAULT_INITIAL_MEAN = 1500.0
    DEFAULT_BETA = 200.0

    def __init__(self, initial_mean=DEFAULT_INITIAL_MEAN,
                       beta=DEFAULT_BETA):

        try:
            self.initial_mean = float(initial_mean)
            self.beta = float(beta)
        except ValueError:
            raise ValueError("EloGameInfo arguments must be numeric")

    def default_rating(self):
        return EloRating(self.initial_mean)

    @staticmethod
    def ensure_game_info(game_info):
        if game_info is None:
            return EloGameInfo()
        elif (not hasattr(game_info, 'initial_mean') or
                not hasattr(game_info, 'beta')):
            if isinstance(game_info, Sequence):
                try:
                    return EloGameInfo(*game_info)
                except TypeError:
                    raise TypeError("game_info must be a sequence of length 0, 1 or 2 or an EloGameInfo object")
            else:
                try:
                    return EloGameInfo(game_info)
                except TypeError:
                    raise TypeError("game_info was passed the wrong number of arguments")
        else:
            return game_info

class EloRating(Rating):
    '''Rating that includes the K value for skill updates'''

    def __init__(self, mean, k_factor=None):
        Rating.__init__(self, mean)
        if k_factor is not None:
            try:
                self.k_factor = float(k_factor)
            except ValueError:
                ValueError("EloRating k_factor value must be numeric")

    def __repr__(self):
        return "EloRating(%s, %s)" % (self.mean, self.k_factor)

    def __str__(self):
        return "mean=%.4f, k_factor=%d" % (self.mean, self.k_factor)

    @staticmethod
    def ensure_rating(rating):
        if not hasattr(rating, 'mean'):
            if isinstance(rating, Sequence):
                try:
                    return EloRating(*rating)
                except TypeError:
                    raise TypeError("EloRating must be a sequence of length 1 or 2 or an EloRating object")
            else:
                try:
                    return EloRating(rating)
                except TypeError:
                    raise TypeError("EloRating was passed the wrong number of arguments")
        else:
            return rating


class EloCalculator(Calculator):
    '''Calculator implementing the Elo algorithm'''

    DEFAULT_K_FACTOR = 32.0 # ICC Default

    score = {WIN: 1.0,
             LOSE: 0.0,
             DRAW: 0.5}

    def __init__(self, k_factor=DEFAULT_K_FACTOR):
        Calculator.__init__(self, Range.exactly(2), Range.exactly(1))
        self.k_factor = k_factor
        RatingFactory.rating_class = EloRating

    def new_ratings(self, teams, game_info=None):
        game_info = EloGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        # ensure sorted by rank
        teams.sort()

        winner, winner_rating = teams[0].player_rating()[0]
        loser, loser_rating = teams[1].player_rating()[0]

        return Match([Team({winner: self.new_rating(winner_rating,
                                                    loser_rating,
                                                    teams.comparison(0, 1),
                                                    game_info)}),
                      Team({loser: self.new_rating(loser_rating,
                                                   winner_rating,
                                                   teams.comparison(1, 0),
                                                   game_info)})])

    def new_rating(self, self_rating, opponent_rating, comparison, game_info=None):
        game_info = EloGameInfo.ensure_game_info(game_info)
        self_mean = self_rating.mean if hasattr(self_rating, 'mean') else self_rating
        opponent_mean = opponent_rating.mean if hasattr(opponent_rating, 'mean') else opponent_rating
        expected_probability = self.expected_score(self_mean, opponent_mean, game_info)
        actual_probability = EloCalculator.score[comparison]
        k = self_rating.k_factor if hasattr(self_rating, 'k_factor') else self.k_factor
        new_rating = self_mean + k * (actual_probability - expected_probability)
        if hasattr(self_rating, 'rating_floor'):
            if new_rating < self_rating.rating_floor:
                new_rating = self_rating.rating_floor
        return EloRating(new_rating, k)

    def expected_score(self, self_rating, opponent_rating, game_info):
        return (1.0 /
                (1.0 + 10.0 ** ((opponent_rating - self_rating) /
                                (2 * game_info.beta))));

    def match_quality(self, teams, game_info=None):
        game_info = EloGameInfo.ensure_game_info(game_info)        
        self.validate_team_and_player_counts(teams)

        teams.sort()

        # The TrueSkill paper mentions that they used s1 - s2 (rating difference) to
        # determine match quality. Moser converts that to a percentage as a delta from 50%
        # using the cumulative density function of the specific curve being used
        expected_score = self.expected_score(teams[0].ratings()[0].mean,
                                             teams[1].ratings()[0].mean,
                                             game_info)
        return (0.5 - abs(expected_score - 0.5)) / 0.5
