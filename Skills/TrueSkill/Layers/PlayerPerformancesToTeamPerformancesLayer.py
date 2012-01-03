from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.FactorGraphs.Schedule import ScheduleStep
from Skills.TrueSkill.Factors.GaussianWeightedSumFactor import GaussianWeightedSumFactor

class PlayerPerformancesToTeamPerformancesLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)

    def build_layer(self):
        for current_team in self.input_variables_groups:
            team_performance = self.create_output_variable(current_team)
            new_sum_factor = self.create_player_to_team_sum_factor(current_team, team_performance)

            self.add_layer_factor(new_sum_factor)

            self.output_variables_groups.append([team_performance])

    def create_prior_schedule(self):
        sequence = self.schedule_sequence(
            map(lambda weighted_sum_factor: ScheduleStep("Perf to Team Perf Step",
                                                         weighted_sum_factor, 0),
                self.local_factors()),
            "all player perf to team perf schedule"
        )
        return sequence

    def create_player_to_team_sum_factor(self, team_members, sum_variable):
        return GaussianWeightedSumFactor(sum_variable, team_members,
                                         [player.key.partial_play_percentage
                                          for player in team_members])

    def create_posterior_schedule(self):
        all_factors = []
        for current_factor in self.local_factors():
            for current_iteration in range(1, len(current_factor.messages)):
                all_factors.append(ScheduleStep("team sum perf @ %s" % current_iteration,
                                                current_factor, current_iteration))
        return self.schedule_sequence(all_factors, "all of the team's sum iteractions")

    def create_output_variable(self, team):
        member_names = [str(player.key) for player in team]
        team_member_names = ", ".join(member_names)
        output_variable = self.parent_factor_graph.variable_factory.create_basic_variable(
            "Team[%s]'s performance" % team_member_names)
        return output_variable
