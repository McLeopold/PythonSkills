from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.TrueSkill.Factors.GaussianWeightedSumFactor import GaussianWeightedSumFactor

class TeamPerformancesToTeamPerformanceDifferencesLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)

    def build_layer(self):
        for i in range(len(self.input_variables_groups) - 1):
            stronger_team = self.input_variables_groups[i][0]
            weaker_team = self.input_variables_groups[i + 1][0]

            current_difference = self.create_output_variable();
            new_differences_factor = self.create_team_performance_to_difference_factor(
                stronger_team,
                weaker_team,
                current_difference)
            self.add_layer_factor(new_differences_factor)

            self.output_variables_groups.append([current_difference])

    def create_team_performance_to_difference_factor(self, stronger_team, weaker_team, output):
        teams = [stronger_team, weaker_team]
        weights = [1.0, -1.0]
        return GaussianWeightedSumFactor(output, teams, weights)

    def create_output_variable(self):
        return self.parent_factor_graph.variable_factory.create_basic_variable(
            "Team performance difference")
