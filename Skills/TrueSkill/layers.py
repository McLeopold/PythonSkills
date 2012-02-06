from skills.factorgraph import (
    FactorGraphLayer,
    ScheduleLoop,
    ScheduleSequence,
    ScheduleStep,
    )

from skills.trueskill.factors import (
    GaussianGreaterThanFactor,
    GaussianLikelihoodFactor,
    GaussianPriorFactor,
    GaussianWeightedSumFactor,
    GaussianWithinFactor,
    )


class IteratedTeamDifferencesInnerLayerError(Exception):
    pass


class TrueSkillFactorGraphLayer(FactorGraphLayer):
    def __init__(self, parent_graph):
        FactorGraphLayer.__init__(self, parent_graph)


class IteratedTeamDifferencesInnerLayer(TrueSkillFactorGraphLayer):
    def __init__(self, parent_graph,
                 team_performances_to_performance_differences,
                 team_differences_comparison_layer):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)
        self.team_performances_to_team_performance_differences = team_performances_to_performance_differences
        self.team_differences_comparison_layer = team_differences_comparison_layer

    def local_factors(self):
        return (self.team_performances_to_team_performance_differences.local_factors() +
                self.team_differences_comparison_layer.local_factors())

    def build_layer(self):
        self.team_performances_to_team_performance_differences.input_variables_groups = self.input_variables_groups
        self.team_performances_to_team_performance_differences.build_layer()

        self.team_differences_comparison_layer.input_variables_groups = self.team_performances_to_team_performance_differences.output_variables_groups
        self.team_differences_comparison_layer.build_layer()

    def create_prior_schedule(self):
        i_len = len(self.input_variables_groups)
        if i_len == 2:
            loop = self.create_two_team_inner_prior_loop_schedule()
        elif i_len > 2:
            loop = self.create_multiple_team_inner_prior_loop_schedule()
        else:
            raise IteratedTeamDifferencesInnerLayerError("IteratedTeamDefferencesInnerLayer must have more than 1 input variables groups")

        total_team_differences = len(self.team_performances_to_team_performance_differences.local_factors())
        #total_teams = total_team_differences + 1

        local_factors = self.team_performances_to_team_performance_differences.local_factors()

        first_differences_factor = local_factors[0]
        last_differences_factor = local_factors[-1]
        inner_schedule = ScheduleSequence(
            "inner schedule",
            [loop,
             ScheduleStep(
                "team_performance_to_performance_difference_factors[0] @ 1",
                first_differences_factor, 1),
             ScheduleStep(
                "team_performance_to_performance_difference_factors[team_team_differences = %d - 1] @ 2" % total_team_differences,
                last_differences_factor, 2)
             ])

        return inner_schedule

    def create_two_team_inner_prior_loop_schedule(self):
        first_perf_to_team_diff = self.team_performances_to_team_performance_differences.local_factors()[0]
        first_team_diff_comparison = self.team_differences_comparison_layer.local_factors()[0]
        items_to_sequence = [
            ScheduleStep(
                "send team perf to perf differences",
                first_perf_to_team_diff, 0
            ),
            ScheduleStep(
                "send to greater than or within factor",
                first_team_diff_comparison, 0
            )
        ]

        return self.schedule_sequence(items_to_sequence, "loop of just two teams inner sequence")

    def create_multiple_team_inner_prior_loop_schedule(self):
        total_team_differences = len(self.team_performances_to_team_performance_differences.local_factors())
        forward_schedule_list = []

        for i in range(total_team_differences - 1):
            current_team_perf_to_team_perf_diff = self.team_performances_to_team_performance_differences.local_factors()[i]
            current_team_diff_comparison = self.team_differences_comparison_layer.local_factors()[i]

            current_forward_schedule_piece = self.schedule_sequence([
                ScheduleStep(
                    "team perf to perf diff %d" % i,
                    current_team_perf_to_team_perf_diff, 0
                ),
                ScheduleStep(
                    "greater than or within result factor %d" % i,
                    current_team_diff_comparison, 0
                ),
                ScheduleStep(
                    "team perf to perf diff factors [%d], 2" % i,
                    current_team_perf_to_team_perf_diff, 2
                )
            ], "current forward schedule piece %d" % i)

            forward_schedule_list.append(current_forward_schedule_piece)

        forward_schedule = ScheduleSequence("forward schedule", forward_schedule_list)

        backward_schedule_list = []
        for i in range(total_team_differences - 1):
            differences_factor = self.team_performances_to_team_performance_differences.local_factors()[-1 - i]
            comparison_factor = self.team_differences_comparison_layer.local_factors()[-1 - i]
            performances_to_differences_factor = self.team_performances_to_team_performance_differences.local_factors()[-1 - i]

            current_backward_schedule_piece = ScheduleSequence(
                "current backward schedule piece",
                [
                 ScheduleStep(
                    "team_performance_to_performance_difference_factors[total_team_differences - 1 - %d] @ 0" % i,
                    differences_factor, 0
                ),
                 ScheduleStep(
                    "greater_than_or_within_result_factors[total_team_differences - 1 - %d] @ 0" % i,
                    comparison_factor, 0
                ),
                 ScheduleStep(
                    "team_performance_to_performance_difference_factors[total_team_differences - 1 - %d] @ 1" % i,
                    performances_to_differences_factor, 1
                )
                ]
            )
            backward_schedule_list.append(current_backward_schedule_piece)

        backward_schedule = ScheduleSequence("backward schedule", backward_schedule_list)

        forward_backward_schedule_to_loop = ScheduleSequence("forward backward schedule to loop", [forward_schedule, backward_schedule])
        initial_max_delta = 0.0001
        loop = ScheduleLoop("loop with max delta of %f" % initial_max_delta,
                            forward_backward_schedule_to_loop,
                            initial_max_delta)

        return loop


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


class TeamDifferencesComparisonLayer(TrueSkillFactorGraphLayer):

    def __init__(self, parent_graph, team_ranks):
        TrueSkillFactorGraphLayer.__init__(self, parent_graph)
        self.team_ranks = team_ranks
        game_info = parent_graph.game_info
        self.epsilon = game_info.draw_margin

    def build_layer(self):
        for i in range(len(self.input_variables_groups)):
            is_draw = self.team_ranks[i] == self.team_ranks[i + 1]
            team_difference = self.input_variables_groups[i][0]
            factor = GaussianWithinFactor(self.epsilon, team_difference) if is_draw else GaussianGreaterThanFactor(self.epsilon, team_difference)
            self.add_layer_factor(factor)


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

