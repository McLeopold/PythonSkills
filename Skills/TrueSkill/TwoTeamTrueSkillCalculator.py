from Skills.Numerics.Range import Range
from Skills.Rating import RatingFactory
from Skills.GaussianRating import GaussianRating
from Skills.Team import Team
from Skills.Teams import Teams
from Skills.SkillCalculator import SkillCalculator
from Skills.TrueSkill.TruncatedGaussianCorrectionFunctions import TruncatedGaussianCorrectionFunctions
from math import sqrt, exp

class TwoTeamTrueSkillCalculator(SkillCalculator):
    '''
    Calculates new ratings for only two teams where each team has 1 or more players.
    '''

    def __init__(self):
        SkillCalculator.__init__(self, Range.exactly(2), Range.at_least(1))
        RatingFactory.rating_class = GaussianRating

    def calculate_new_ratings(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)
        teams.sort()

        return Teams(self.calculate_new_team_ratings(game_info, teams[0], teams[1],
                                                     teams.comparison()),
                     self.calculate_new_team_ratings(game_info, teams[1], teams[0],
                                                     teams.comparison(False)))

    def calculate_new_team_ratings(self, game_info, self_team, other_team,
                                   self_to_other_team_comparison):
        self_mean_sum = sum(rating.mean for rating in self_team.ratings())
        other_team_mean_sum = sum(rating.mean for rating in other_team.ratings())
        if self_to_other_team_comparison == Teams.LOSE:
            mean_delta = other_team_mean_sum - self_mean_sum
        else:
            mean_delta = self_mean_sum - other_team_mean_sum

        c = sqrt(
            sum(rating.stdev ** 2.0 for rating in self_team.ratings()) +
            sum(rating.stdev ** 2.0 for rating in other_team.ratings()) +
            (len(self_team) + len(other_team)) * game_info.beta ** 2
        )
        tau_squared = game_info.dynamics_factor ** 2

        if self_to_other_team_comparison != Teams.DRAW:
            v = TruncatedGaussianCorrectionFunctions.v_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0 * self_to_other_team_comparison
        else:
            v = TruncatedGaussianCorrectionFunctions.v_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0

        new_team_ratings = Team()

        for self_team_current_player, previous_player_rating in self_team.player_rating():
            mean_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / c
            std_dev_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / (c ** 2.0)

            player_mean_delta = rank_multiplier * mean_multiplier * v
            new_mean = previous_player_rating.mean + player_mean_delta

            new_std_dev = sqrt(
                (previous_player_rating.stdev ** 2.0 + tau_squared) * (1.0 - w * std_dev_multiplier)
            )

            new_team_ratings[self_team_current_player] = GaussianRating(new_mean, new_std_dev)

        return new_team_ratings

    def calculate_match_quality(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        team1ratings = teams[0].ratings()
        team2ratings = teams[1].ratings()

        total_players = sum(len(team) for team in teams)

        beta_squared = game_info.beta ** 2.0

        team1mean_sum = sum(player.mean for player in team1ratings)
        team1std_dev_squared = sum(player.stdev ** 2.0 for player in team1ratings)

        team2mean_sum = sum(player.mean for player in team2ratings)
        team2std_dev_squared = sum(player.stdev ** 2.0 for player in team2ratings)

        sqrt_part = sqrt(
            (total_players * beta_squared) /
            (total_players * beta_squared + team1std_dev_squared + team2std_dev_squared)
        )

        exp_part = exp(
            (-1.0 * (team1mean_sum - team2mean_sum) ** 2.0) /
            (2.0 * (total_players * beta_squared + team1std_dev_squared + team2std_dev_squared))
        )

        return exp_part * sqrt_part
