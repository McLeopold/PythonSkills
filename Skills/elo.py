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


class EloRating(Rating):
    '''Rating that includes the K value for skill updates'''

    DEFAULT_K_FACTOR = 32.0 # ICC Default

    def __init__(self, mean, k_factor=DEFAULT_K_FACTOR):
        Rating.__init__(self, mean)
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
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'k_factor')):
            if isinstance(rating, Sequence):
                try:
                    return EloRating(*rating)
                except TypeError:
                    raise TypeError("EloRating must be a sequence of length 1 or 2 or a EloRating object")
            else:
                try:
                    return EloRating(rating)
                except TypeError:
                    raise TypeError("EloRating was passed the wrong number of arguments")
        else:
            return rating


class EloCalculator(Calculator):
    '''Calculator implementing the Elo algorithm'''

    score = {WIN: 1.0,
             LOSE: 0.0,
             DRAW: 0.5}

    def __init__(self, k_factor=EloRating.DEFAULT_K_FACTOR):
        Calculator.__init__(self, Range.exactly(2), Range.exactly(1))
        self.k_factor = k_factor
        RatingFactory.rating_class = EloRating


    def new_ratings(self, game_info, teams):
        self.validate_team_and_player_counts(teams)

        # ensure sorted by rank
        teams.sort()

        winner, winner_rating = teams[0].player_rating()[0]
        loser, loser_rating = teams[1].player_rating()[0]

        return Match([Team({winner: self.new_rating(game_info,
                                                             winner_rating.mean,
                                                             loser_rating.mean,
                                                             teams.comparison(0, 1))}),
                      Team({loser: self.new_rating(game_info,
                                                            loser_rating.mean,
                                                            winner_rating.mean,
                                                            teams.comparison(1, 0))})])

    def new_rating(self, game_info, self_rating, opponent_rating, comparison):
        expected_probability = self.expected_score(game_info, self_rating, opponent_rating)
        actual_probability = EloCalculator.score[comparison]
        if hasattr(self_rating, 'k_factor'):
            k = self_rating.k_factor
        else:
            k = self.k_factor
        new_rating = self_rating + k * (actual_probability - expected_probability)
        if hasattr(self_rating, 'rating_floor'):
            if new_rating < self_rating.rating_floor:
                new_rating = self_rating.rating_floor
        return EloRating(new_rating)

    def expected_score(self, game_info, self_rating, opponent_rating):
        return (1.0 /
                (1.0 + 10.0 ** ((opponent_rating - self_rating) /
                                (2 * game_info.beta))));

    def match_quality(self, game_info, teams):
        self.validate_team_and_player_counts(teams)

        teams.sort()

        # The TrueSkill paper mentions that they used s1 - s2 (rating difference) to
        # determine match quality. Moser converts that to a percentage as a delta from 50%
        # using the cumulative density function of the specific curve being used
        expected_score = self.expected_score(game_info,
                                             teams[0].ratings()[0].mean,
                                             teams[1].ratings()[0].mean)
        return (0.5 - abs(expected_score - 0.5)) / 0.5
