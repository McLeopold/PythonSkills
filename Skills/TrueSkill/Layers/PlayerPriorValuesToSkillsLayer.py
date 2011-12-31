from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.FactorGraphs.Schedule import ScheduleSequence, ScheduleStep
from Skills.TrueSkill.Factors.GaussianPriorFactor import GaussianPriorFactor

class PlayerPriorValuesToSkillsLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph, teams):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)
        self.teams = teams

    def build_layer(self):
        for current_team in self.teams:
            current_team_skills = []
            for current_team_player in current_team.players():
                player_skill = self.create_skill_output_variable(current_team_player)
                prior_factor = self.create_prior_factor(current_team_player, current_team[current_team_player], player_skill)
                self.add_layer_factor(prior_factor)
                current_team_skills.append(player_skill)

            self.output_variables_groups.append(current_team_skills)

    def create_prior_schedule(self):
        return self.schedule_sequence(map(lambda prior: ScheduleStep("Prior to Skill Step", prior, 0),
                                          self.local_factors()),
                                      "All priors")

    def create_prior_factor(self, player, prior_rating, skills_variable):
        return GaussianPriorFactor(prior_rating.mean,
                                   (prior_rating.stdev ** 2 +
                                    self.parent_factor_graph.game_info.dynamics_factor ** 2),
                                   skills_variable)

    def create_skill_output_variable(self, key):
        return self.parent_factor_graph.variable_factory.create_keyed_variable(key, "%s's skill" % key)
