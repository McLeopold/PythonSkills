from Skills.FactorGraphs.FactorGraph import FactorGraph
from Skills.TrueSkill.Layers.PlayerPriorValuesToSkillsLayer import PlayerPriorValuesToSkillsLayer
from Skills.FactorGraphs.VariableFactory import VariableFactory
from Skills.Numerics.Gaussian import Gaussian
from Skills.TrueSkill.Layers.PlayerSkillsToPerformancesLayer import PlayerSkillsToPerformancesLayer
from Skills.TrueSkill.Layers.PlayerPerformancesToTeamPerformancesLayer import PlayerPerformancesToTeamPerformancesLayer
from Skills.TrueSkill.Layers.IteratedTeamDifferencesInnerLayer import IteratedTeamDefferencesInnerLayer
from Skills.TrueSkill.Layers.TeamPerformancesToTeamPerformanceDifferencesLayer import TeamPerformancesToTeamPerformanceDifferencesLayer
from Skills.TrueSkill.Layers.TeamDifferencesComparisonLayer import TeamDifferencesComparisonLayer
from Skills.FactorGraphs.FactorList import FactorList
from Skills.FactorGraphs.Schedule import ScheduleSequence
from Skills.Team import Team
from Skills.Match import Match
from math import exp
from Skills.GaussianRating import GaussianRating

class TrueSkillFactorGraph(FactorGraph):

    def __init__(self, game_info, teams, team_ranks):
        self.prior_layer = PlayerPriorValuesToSkillsLayer(self, teams)
        self.game_info = game_info
        new_factory = VariableFactory(lambda: Gaussian.from_precision_mean(0.0, 0.0))
        self.variable_factory = new_factory
        self.layers = [
            self.prior_layer,
            PlayerSkillsToPerformancesLayer(self),
            PlayerPerformancesToTeamPerformancesLayer(self),
            IteratedTeamDefferencesInnerLayer(self,
                                              TeamPerformancesToTeamPerformanceDifferencesLayer(self),
                                              TeamDifferencesComparisonLayer(self, team_ranks))
        ]

    def build_graph(self):
        last_output = None

        for current_layer in self.layers:
            if last_output is not None:
                current_layer.input_variables_groups = last_output
            current_layer.build_layer()
            last_output = current_layer.output_variables_groups

    def run_schedule(self):
        full_schedule = self.create_full_schedule()
        full_schedule.visit()

    def probability_of_ranking(self):
        factor_list = FactorList()

        for current_layer in self.layers:
            for local_factor in current_layer.local_factors():
                factor_list.append(local_factor)

        log_z = factor_list.log_normalization()
        return exp(log_z)

    def create_full_schedule(self):
        full_schedule = []

        for current_layer in self.layers:
            current_prior_schedule = current_layer.create_prior_schedule()
            if current_prior_schedule is not None:
                full_schedule.append(current_prior_schedule)

        for current_layer in reversed(self.layers):
            current_posterior_schedule = current_layer.create_posterior_schedule()
            if current_posterior_schedule is not None:
                full_schedule.append(current_posterior_schedule)

        return ScheduleSequence("Full schedule", full_schedule)

    def updated_ratings(self):
        results = Match()

        for current_team in self.prior_layer.output_variables_groups:
            team_results = Team()
            for current_player, current_player_rating in [(player.key, player.value) for player in current_team]:
                new_rating = GaussianRating(current_player_rating.mean,
                                            current_player_rating.stdev)
                team_results[current_player] = new_rating
            results.append(team_results)

        return results
