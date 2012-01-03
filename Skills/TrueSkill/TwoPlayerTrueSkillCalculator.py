from Skills.SkillCalculator import SkillCalculator
from Skills.Numerics.Range import Range
from Skills.TrueSkill.TruncatedGaussianCorrectionFunctions import TruncatedGaussianCorrectionFunctions
from Skills.Rating import Rating
from Skills.Team import Team
from Skills.Teams import Teams
from math import sqrt, exp

class TwoPlayerTrueSkillCalculator(SkillCalculator):
    def __init__(self):
        SkillCalculator.__init__(self, Range.exactly(2), Range.exactly(1))

    def calculate_new_ratings(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        # ensure sorted by rank
        teams.sort()

        winning_team_players = teams[0].players()
        winner = winning_team_players[0]
        winner_previous_rating = teams[0][winner]

        losing_team_players = teams[1].players()
        loser = losing_team_players[0]
        loser_previous_rating = teams[1][loser]

        return Teams(Team(winner, self.calculate_new_rating(game_info,
                                                            winner_previous_rating,
                                                            loser_previous_rating,
                                                            teams.comparison())),
                     Team(loser, self.calculate_new_rating(game_info,
                                                           loser_previous_rating,
                                                           winner_previous_rating,
                                                           teams.comparison(False))))

    def calculate_new_rating(self, game_info, self_rating, opponent_rating, comparison):
        if comparison == Teams.LOSE:
            mean_delta = opponent_rating.mean - self_rating.mean
        else:
            mean_delta = self_rating.mean - opponent_rating.mean

        c = sqrt(
            self_rating.stdev ** 2.0 +
            opponent_rating.stdev ** 2.0 +
            2.0 * game_info.beta ** 2.0
        )

        if comparison != Teams.DRAW:
            v = TruncatedGaussianCorrectionFunctions.v_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = float(comparison)
        else:
            v = TruncatedGaussianCorrectionFunctions.v_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0

        mean_multiplier = (self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0) / c

        variance_with_dynamics = self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0
        std_dev_multiplier = variance_with_dynamics / (c ** 2.0)

        new_mean = self_rating.mean + (rank_multiplier * mean_multiplier * v)
        new_std_dev = sqrt(variance_with_dynamics * (1.0 - w * std_dev_multiplier))

        return Rating(new_mean, new_std_dev)

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
