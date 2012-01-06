from Skills.Numerics.Range import Range
from Skills.Rating import RatingFactory
from Skills.GaussianRating import GaussianRating
from Skills.Team import Team
from Skills.Match import Match
from Skills.SkillCalculator import SkillCalculator
from Skills.TrueSkill.TruncatedGaussianCorrectionFunctions import TruncatedGaussianCorrectionFunctions
from math import sqrt, exp

class TwoPlayerTrueSkillCalculator(SkillCalculator):

    score = {Match.WIN: 1.0,
             Match.LOSE:-1.0,
             Match.DRAW: 0.0}

    def __init__(self):
        SkillCalculator.__init__(self, Range.exactly(2), Range.exactly(1))
        RatingFactory.rating_class = GaussianRating

    def calculate_new_ratings(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        # ensure sorted by rank
        teams.sort()

        winner, winner_rating = teams[0].player_rating()[0]
        loser, loser_rating = teams[1].player_rating()[0]

        return Match([Team({winner: self.calculate_new_rating(game_info,
                                                             winner_rating,
                                                             loser_rating,
                                                             teams.comparison(0, 1))}),
                      Team({loser: self.calculate_new_rating(game_info,
                                                            loser_rating,
                                                            winner_rating,
                                                            teams.comparison(1, 0))})])

    def calculate_new_rating(self, game_info, self_rating, opponent_rating, comparison):
        if comparison == Match.LOSE:
            mean_delta = opponent_rating.mean - self_rating.mean
        else:
            mean_delta = self_rating.mean - opponent_rating.mean

        c = sqrt(
            self_rating.stdev ** 2.0 +
            opponent_rating.stdev ** 2.0 +
            2.0 * game_info.beta ** 2.0
        )

        if comparison != Match.DRAW:
            v = TruncatedGaussianCorrectionFunctions.v_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = TwoPlayerTrueSkillCalculator.score[comparison]
        else:
            v = TruncatedGaussianCorrectionFunctions.v_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0

        mean_multiplier = (self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0) / c

        variance_with_dynamics = self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0
        std_dev_multiplier = variance_with_dynamics / (c ** 2.0)

        new_mean = self_rating.mean + (rank_multiplier * mean_multiplier * v)
        new_std_dev = sqrt(variance_with_dynamics * (1.0 - w * std_dev_multiplier))

        return GaussianRating(new_mean, new_std_dev)

    def calculate_match_quality(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        player1rating, player2rating = [team.ratings()[0] for team in teams]

        twice_beta_squared = 2.0 * game_info.beta ** 2.0
        player1sigma_squared = player1rating.stdev ** 2.0
        player2sigma_squared = player2rating.stdev ** 2.0

        sqrt_part = sqrt(
            twice_beta_squared / (twice_beta_squared + player1sigma_squared + player2sigma_squared)
        )

        exp_part = exp(
            (-1.0 * (player1rating.mean - player2rating.mean) ** 2.0) /
            (2.0 * (twice_beta_squared + player1sigma_squared + player2sigma_squared))
        )

        return sqrt_part * exp_part
