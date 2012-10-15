from collections import Sequence, defaultdict
from math import sqrt, log, pi

from skills import (
    GaussianRating,
    Calculator,
    Match,
    RatingFactory,
    Team,
    WIN,
    LOSE,
    DRAW,
    )

from skills.numerics import Range


class GlickoGameInfo(object):
    '''Parameters about the game used for calculating new skills'''

    DEFAULT_INITIAL_MEAN = 1500.0
    DEFAULT_BETA = 200.0

    def __init__(self, initial_mean=DEFAULT_INITIAL_MEAN,
                       beta=DEFAULT_BETA):

        try:
            self.initial_mean = float(initial_mean)
            self.beta = float(beta)
        except ValueError:
            raise ValueError("GlickoGameInfo arguments must be numeric")

    def default_rating(self):
        return GlickoRating(self.initial_mean)

    @staticmethod
    def ensure_game_info(game_info):
        if game_info is None:
            return GlickoGameInfo()
        elif (not hasattr(game_info, 'initial_mean') or
                not hasattr(game_info, 'beta')):
            if isinstance(game_info, Sequence):
                try:
                    return GlickoGameInfo(*game_info)
                except TypeError:
                    raise TypeError("game_info must be a sequence of length 0, 1 or 2 or an GlickoGameInfo object")
            else:
                try:
                    return GlickoGameInfo(game_info)
                except TypeError:
                    raise TypeError("game_info was passed the wrong number of arguments")
        else:
            return game_info


class GlickoRating(GaussianRating):
    '''Rating that includes a mean, standard deviation and last update period'''

    def __init__(self, mean, stdev, last_rating_period=None):
        GaussianRating.__init__(self, mean, stdev)
        self.last_rating_period = last_rating_period

    def __repr__(self):
        return "GlickoRating(%s, %s, %s)" % (self.mean, self.stdev, self.last_rating_period)

    def __str__(self):
        return "mean=%.4f, stdev=%.4f, last_rating_period=%d" % (self.mean, self.stdev, self.last_rating_period)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'stdev') or
                not hasattr(rating, 'last_rating_period')):
            if isinstance(rating, Sequence):
                try:
                    return GlickoRating(*rating)
                except TypeError:
                    raise TypeError("GlickoRating must be a sequence of length 2 or 3 or a GlickoRating object")
            else:
                try:
                    return GlickoRating(rating)
                except TypeError:
                    raise TypeError("GlickoRating was passed the wrong number of arguments")
        else:
            return rating


class GlickoCalculator(Calculator):
    '''
    Implements Glicko calculator
    
    See http://www.glicko.net/research/gdescrip.pdf for details
    '''

    score = {WIN: 1.0,
             LOSE: 0.0,
             DRAW: 0.5}

    def __init__(self, c_factor=None):
        Calculator.__init__(self, Range .exactly(2), Range.exactly(1))
        self.c_factor = c_factor
        RatingFactory.rating_class = GlickoRating

    def new_ratings(self, matches, rating_period=None, game_info=None):
        game_info = GlickoGameInfo.ensure_game_info(game_info)
        # get unique list of players and ensure ratings are consistant
        players = {}
        opponents = defaultdict(list)
        player_RD = {}

        # Step 1: calculate r and RD for onset of rating period
        # also cache values of g(RDj) and E(s|r, rj, RDj) for each player
        for match in matches:
            # ensure winning team is team 0
            match.sort()
            for player, rating in match.player_rating():
                if player in players:
                    if rating != players[player]:
                        raise ValueError("Inconsistant ratings: player %s has rating %s and rating %s" % (player, rating, players[player]))
                else:
                    # calc new RD from old RD
                    if (self.c_factor is None or
                            rating.last_rating_period is None or
                            rating_period is None):
                        player_RD[player] = rating.stdev
                    else:
                        t = rating_period - rating.last_rating_period
                        if t <= 0:
                            raise ValueError("Player %s has a last_rating_period equal to the current rating_period" % (player))
                        player_RD[player] = min(game_info.beta, sqrt(rating.stdev ** 2 + self.c_factor * t))
                    players[player] = rating

            # create opponent lists of players and outcomes
            player1 = match[0].players()[0]
            player2 = match[1].players()[0]
            opponents[player1].append((player2, GlickoCalculator.score[match.comparison(0, 1)]))
            opponents[player2].append((player1, GlickoCalculator.score[match.comparison(1, 0)]))


        # Step 2: carry out the update calculations for each player separately
        q = log(10.0) / 400.0
        def g(RD):
            return 1.0 / sqrt(1.0 + 3.0 * q ** 2.0 * (RD ** 2.0) / pi ** 2.0)

        def E(r, rj, RDj):
            return 1.0 / (1.0 + pow(10.0, -g(RDj) * (r - rj) / 400.0))

        def d2(g_RD, E_sr_r_RD):
            return pow(q ** 2.0 * sum(
                g_RD[j] ** 2.0 * E_sr_r_RD[j] * (1.0 - E_sr_r_RD[j])
                for j in range(len(g_RD))
            ), -1.0)

        new_ratings = Match()
        for player, rating in players.items():
            # cache values of g(RDj) and E(s|r, r, RDj) for each opponent
            opponent_g_RD = []
            opponent_E_sr_r_RD = []
            opponent_s = []
            for opponent, score in opponents[player]:
                opponent_g_RD.append(g(player_RD[opponent]))
                opponent_E_sr_r_RD.append(E(rating.mean, players[opponent].mean, player_RD[opponent]))
                opponent_s.append(score)

            # cache value, this form used twice in the paper 
            RD2_d2 = (1.0 / player_RD[player] ** 2.0 +
                      1.0 / d2(opponent_g_RD, opponent_E_sr_r_RD))

            # new rating value
            r_new = (rating.mean + q / RD2_d2 * sum(
                opponent_g_RD[j] * (opponent_s[j] - opponent_E_sr_r_RD[j])
                for j in range(len(opponent_s))
            ))
            # new rating deviation value
            RD_new = sqrt(pow(RD2_d2, -1))

            new_ratings.append(Team({player: GlickoRating(r_new, RD_new, rating_period)}))

        return new_ratings

    def expected_score(self, self_rating, opponent_rating, game_info):
        return (1.0 /
                (1.0 + 10.0 ** ((opponent_rating - self_rating) /
                                (2 * game_info.beta))));

    def match_quality(self, teams, game_info=None):
        game_info = GlickoGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        teams.sort()

        # The TrueSkill paper mentions that they used s1 - s2 (rating difference) to
        # determine match quality. Moser converts that to a percentage as a delta from 50%
        # using the cumulative density function of the specific curve being used
        expected_score = self.expected_score(teams[0].ratings()[0].mean,
                                             teams[1].ratings()[0].mean,
                                             game_info)
        return (0.5 - abs(expected_score - 0.5)) / 0.5
