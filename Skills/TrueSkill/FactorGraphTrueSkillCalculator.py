from Skills.SkillCalculator import SkillCalculator, SkillCalculatorSupportedOptions
from Skills.Numerics.Range import Range
from Skills.TrueSkill.TrueSkillFactorGraph import TrueSkillFactorGraph
from Skills.Numerics.Matrix import DiagonalMatrix, Matrix
from Skills.PartialPlay import PartialPlay
from math import sqrt, exp

class FactorGraphTrueSkillCalculator(SkillCalculator):
    '''
    Calculates TrueSkill using a full factor graph.
    '''

    def __init__(self):
        SkillCalculator.__init__(self,
                                 (SkillCalculatorSupportedOptions.PARTIAL_PLAY |
                                  SkillCalculatorSupportedOptions.PARTIAL_UPDATE),
                                 Range.at_least(2), Range.at_least(1))

    def calculate_new_ratings(self, game_info, teams):
        self.validate_team_count_and_players_count_per_team(teams)

        # ensure sorted by rank
        teams.sort()

        factor_graph = TrueSkillFactorGraph(game_info, teams, teams.rank)
        factor_graph.build_graph()
        factor_graph.run_schedule()

        #probability_of_outcome = factor_graph.probability_of_ranking()

        return factor_graph.updated_ratings()

    def calculate_match_quality(self, game_info, teams):
        skills_matrix = DiagonalMatrix([rating.stdev ** 2
                                            for team in teams
                                                for rating in team.ratings()])
        mean_vector_transpose = Matrix([[rating.mean
                                 for team in teams
                                     for rating in team.ratings()]])
        mean_vector = mean_vector_transpose.transpose()

        player_teams_matrix = self.create_player_team_assignment_matrix(teams)
        player_teams_matrix_transpose = player_teams_matrix.transpose()

        beta_squared = game_info.beta ** 2

        start = mean_vector_transpose * player_teams_matrix
        aTa = (beta_squared * player_teams_matrix_transpose) * player_teams_matrix
        aTSA = (player_teams_matrix_transpose * skills_matrix) * player_teams_matrix

        middle = aTa + aTSA

        middle_inverse = middle.inverse()

        end = player_teams_matrix_transpose * mean_vector

        exp_part_matrix = (-0.5 * ((start * middle_inverse) * end))
        exp_part = exp_part_matrix.determinant()

        sqrt_part_numerator = aTa.determinant()
        sqrt_part_denominator = middle.determinant()
        sqrt_part = sqrt_part_numerator / sqrt_part_denominator

        result = exp(exp_part) * sqrt(sqrt_part)

        return result

    def create_player_team_assignment_matrix(self, teams):
        total_players = sum(len(team) for team in teams)
        player_assignments = []
        total_previous_players = 0

        team_assignments_list_count = len(teams)
        for current_column in range(team_assignments_list_count - 1):
            player_assignments.append([])
            current_team = teams[current_column]
            player_assignments[current_column] = [0] * total_previous_players
            for current_player in current_team.players():
                player_assignments[current_column].append(PartialPlay.partial_play_percentage(current_player))
                total_previous_players += 1
            rows_remaining = total_players - total_previous_players
            next_team = teams[current_column + 1]
            for next_team_player in next_team.players():
                player_assignments[current_column].append(-1.0 * PartialPlay.partial_play_percentage(next_team_player))
                rows_remaining -= 1
            player_assignments[current_column].extend([0.0] * rows_remaining)

        return Matrix(player_assignments).transpose()
