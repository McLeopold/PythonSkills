from Skills.SkillCalculator import SkillCalculator
from Skills.Numerics.Range import Range
from Skills.Match import Match
from Skills.GaussianRating import GaussianRating
from Skills.Glicko.GlickoRating import GlickoRating
from Skills.Rating import RatingFactory
from math import sqrt, log, pi, pow
from collections import defaultdict
from Skills.Team import Team

class GlickoCalculatorError(Exception):
    pass

class GlickoCalculator(SkillCalculator):
    '''
    Implements Glicko calculator
    
    See http://www.glicko.net/research/gdescrip.pdf for details
    '''

    score = {Match.WIN: 1.0,
             Match.LOSE: 0.0,
             Match.DRAW: 0.5}

    def __init__(self, c=None):
        SkillCalculator.__init__(self, Range.exactly(2), Range.exactly(1))
        self.c = c
        RatingFactory.rating_class = GlickoRating

    def calculate_new_ratings(self, game_info, matches, rating_period):
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
                        raise GlickoCalculatorError("Inconsistant ratings: player %s has rating %s and rating %s" % (player, rating, players[player]))
                else:
                    # calc new RD from old RD
                    if self.c is None or rating.last_rating_period is None:
                        player_RD[player] = rating.stdev
                    else:
                        t = rating_period - rating.last_rating_period
                        if t <= 0:
                            raise GlickoCalculatorError("Player %s has a last_rating_period equal to the current rating_period" % (player))
                        player_RD[player] = min(game_info.beta, sqrt(rating.stdev ** 2 + self.c * t))
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

        def d2(r, g_RD, E_sr_r_RD):
            return pow(q ** 2.0 * sum(
                g_RD[j] ** 2.0 * E_sr_r_RD[j] * (1.0 - E_sr_r_RD[j])
                for j in range(len(g_RD))
            ), -1.0)

        new_ratings = Match()
        for player, rating in match.player_rating():
            # cache values of g(RDj) and E(s|r, r, RDj) for each opponent
            opponent_g_RD = []
            opponent_E_sr_r_RD = []
            opponent_s = []
            for j, (opponent, score) in enumerate(opponents[player]):
                opponent_g_RD.append(g(player_RD[opponent]))
                opponent_E_sr_r_RD.append(E(rating.mean, players[opponent].mean, player_RD[opponent]))
                opponent_s.append(score)

            # cache value, this form used twice in the paper 
            RD2_d2 = (1.0 / player_RD[player] ** 2.0 +
                      1.0 / d2(rating.mean, opponent_g_RD, opponent_E_sr_r_RD))

            # new rating value
            r_new = (rating.mean + q / RD2_d2 * sum(
                opponent_g_RD[j] * (opponent_s[j] - opponent_E_sr_r_RD[j])
                for j in range(len(opponent_s))
            ))
            # new rating deviation value
            RD_new = sqrt(pow(RD2_d2, -1))

            new_ratings.append(Team({player: GlickoRating(r_new, RD_new, rating_period)}))

        return new_ratings

    def calculate_match_quality(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        teams.sort()

        # The TrueSkill paper mentions that they used s1 - s2 (rating difference) to
        # determine match quality. Moser converts that to a percentage as a delta from 50%
        # using the cumulative density function of the specific curve being used
        expected_score = self.expected_score(game_info,
                                             teams[0].ratings()[0].mean,
                                             teams[1].ratings()[0].mean)
        return (0.5 - abs(expected_score - 0.5)) / 0.5
