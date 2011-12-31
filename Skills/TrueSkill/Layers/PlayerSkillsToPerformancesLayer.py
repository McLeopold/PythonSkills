from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.TrueSkill.Factors.GaussianLikelihoodFactor import GaussianLikelihoodFactor
from Skills.FactorGraphs.Schedule import ScheduleStep

class PlayerSkillsToPerformancesLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)

    def build_layer(self):
        for current_team in self.input_variables_groups:
            current_team_player_performances = []
            for player_skill_variable in current_team:
                current_player = player_skill_variable.key
                player_performance = self.create_output_variable(current_player)
                new_likelihood_factor = self.create_likelihood(player_skill_variable, player_performance)
                self.add_layer_factor(new_likelihood_factor)
                current_team_player_performances.append(player_performance)
            self.output_variables_groups.append(current_team_player_performances)

    def create_likelihood(self, player_skill, player_performance):
        return GaussianLikelihoodFactor(self.parent_factor_graph.game_info.beta ** 2,
                                        player_performance, player_skill)

    def create_output_variable(self, key):
        return self.parent_factor_graph.variable_factory.create_keyed_variable(key, "%s's performance" % key)

    def create_prior_schedule(self):
        return self.schedule_sequence(map(lambda likelihood: ScheduleStep("Skill to Perf step", likelihood, 0),
                                          self.local_factors()),
                                      "All skill to performance sending")

    def create_posterior_schedule(self):
        return self.schedule_sequence(map(lambda likelihood: ScheduleStep("name", likelihood, 1),
                                          self.local_factors()),
                                      "All skill to performance sending")
