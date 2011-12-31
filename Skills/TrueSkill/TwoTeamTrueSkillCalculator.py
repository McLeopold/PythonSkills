from Skills.SkillCalculator import SkillCalculator
from Skills.Numerics.Range import Range
from Skills.TrueSkill.DrawMargin import DrawMargin
from Skills.PairwiseComparison import PairwiseComparison
from Skills.TrueSkill.TruncatedGaussianCorrectionFunctions import TruncatedGaussianCorrectionFunctions
from Skills.Rating import Rating
from Skills.Team import Team
from math import sqrt, exp

class TwoTeamTrueSkillCalculator(SkillCalculator):
    '''
    Calculates new ratings for only two teams where each team has 1 or more players.
    '''

    def __init__(self):
        SkillCalculator.__init__(self, None, Range.exactly(2), Range.at_least(1))

    def calculate_new_ratings(self, game_info, teams, team_ranks):
        self.validate_team_count_and_players_count_per_team(teams)

        # ensure sorted by rank
        team_ranks, teams = zip(*sorted(zip(team_ranks, teams)))
        team_ranks = list(team_ranks)
        teams = list(teams)

        team1 = teams[0]
        team2 = teams[1]

        was_draw = team_ranks[0] == team_ranks[1]

        results = Team()

        self.update_player_ratings(game_info,
                                   results,
                                   team1,
                                   team2,
                                   PairwiseComparison.DRAW if was_draw else PairwiseComparison.WIN)
        self.update_player_ratings(game_info,
                                   results,
                                   team2,
                                   team1,
                                   PairwiseComparison.DRAW if was_draw else PairwiseComparison.LOSE)

        return results

    def update_player_ratings(self, game_info, new_player_ratings,
                              self_team, other_team,
                              self_to_other_team_comparison):
        draw_margin = DrawMargin.draw_margin_from_draw_probability(game_info.draw_probability, game_info.beta)

        beta_squared = game_info.beta ** 2
        tau_squared = game_info.gynamics_factor ** 2

        total_players = len(self_team) + len(other_team)

        self_mean_sum = sum(rating.mean for rating in self_team.ratings())
        other_team_mean_sum = sum(rating.mean for rating in other_team.ratings())

        c = sqrt(
            sum(rating.stdev for rating in self_team.ratings()) +
            sum(rating.stdev for rating in other_team.ratings()) +
            total_players * beta_squared
        )

        winning_mean, losing_mean = (other_team_mean_sum, self_mean_sum
                                     if self_to_other_team_comparison == PairwiseComparison.LOSE else
                                     self_mean_sum, other_team_mean_sum)

        mean_delta = winning_mean - losing_mean

        if self_to_other_team_comparison != PairwiseComparison.DRAW:
            v = TruncatedGaussianCorrectionFunctions.v_exceeds_margin_scaled(mean_delta, draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_exceeds_margin_scaled(mean_delta, draw_margin, c)
            rank_multiplier = 1.0 * self_to_other_team_comparison
        else:
            v = TruncatedGaussianCorrectionFunctions.v_within_margin_scaled(mean_delta, draw_margin, c)
            w = TruncatedGaussianCorrectionFunctions.w_within_margin_scaled(mean_delta, draw_margin, c)
            rank_multiplier = 1.0

        for self_team_current_player, previous_player_rating in self_team.player_rating():
            mean_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / c
            std_dev_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / (c ** 2.0)

            player_mean_delta = rank_multiplier * mean_multiplier * v
            new_mean = previous_player_rating.mean + player_mean_delta

            new_std_dev = sqrt(
                (previous_player_rating.stdev ** 2.0 + tau_squared) * (1.0 - w * std_dev_multiplier)
            )

            new_player_ratings[self_team_current_player] = Rating(new_mean, new_std_dev)

    def calculate_match_quality(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        team1ratings = teams[0].ratings()
        team1count = len(team1ratings)

        team2ratings = teams[1].ratings()
        team2count = len(team2ratings)

        total_players = team1count + team2count

        beta_squared = game_info.beta ** 2.0

        team1mean_sum = sum(player.mean for player in team1ratings)
        team1std_dev_squared = sum(player.stdev for player in team1ratings)

        team2mean_sum = sum(player.mean for player in team2ratings)
        team2std_dev_squared = sum(player.stdev for player in team2ratings)

        sqrt_part = sqrt(
            total_players * beta_squared /
            (total_players * beta_squared + team1std_dev_squared + team2std_dev_squared)
        )

        exp_part = exp(
            (-1.0 * (team1mean_sum - team2mean_sum) ** 2.0) /
            (2.0 * (total_players * beta_squared + team1std_dev_squared + team2std_dev_squared))
        )

        return exp_part * sqrt_part
