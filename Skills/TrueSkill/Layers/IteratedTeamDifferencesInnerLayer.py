from Skills.TrueSkill.Layers.TrueSkillFactorGraphLayer import TrueSkillFactorGraphLayer
from Skills.FactorGraphs.Schedule import ScheduleSequence, ScheduleStep, \
    Schedule, ScheduleLoop

class IteratedTeamDefferencesInnerLayerError(Exception):
    pass

class IteratedTeamDefferencesInnerLayer(TrueSkillFactorGraphLayer):
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
            raise IteratedTeamDefferencesInnerLayerError("IteratedTeamDefferencesInnerLayer must have more than 1 input variables groups")

        total_team_differences = len(self.team_performances_to_team_performance_differences.local_factors())
        total_teams = total_team_differences + 1

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


