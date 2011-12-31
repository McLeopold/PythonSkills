from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.TrueSkill.DrawMargin import DrawMargin
from Skills.TrueSkill.Factors.GaussianWithinFactor import GaussianWithinFactor
from Skills.TrueSkill.Factors.GaussianGreaterThanFactor import GaussianGreaterThanFactor

class TeamDifferencesComparisonLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph, team_ranks):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)
        self.team_ranks = team_ranks
        game_info = parent_graph.game_info
        self.epsilon = DrawMargin.draw_margin_from_draw_probability(game_info.draw_probability,
                                                                    game_info.beta)
    def build_layer(self):
        for i in range(len(self.input_variables_groups)):
            is_draw = self.team_ranks[i] == self.team_ranks[i + 1]
            team_difference = self.input_variables_groups[i][0]
            factor = GaussianWithinFactor(self.epsilon, team_difference) if is_draw else GaussianGreaterThanFactor(self.epsilon, team_difference)
            self.add_layer_factor(factor)
