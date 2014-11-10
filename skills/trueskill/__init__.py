from math import sqrt, exp

from collections import Sequence

from skills import (
    Calculator,
    Match,
    RatingFactory,
    GaussianRating,
    Team,
    WIN,
    LOSE,
    DRAW,
    )

from skills.numerics import (
    Range,
    Gaussian,
    Matrix,
    DiagonalMatrix,
    )

from skills.factorgraph import (
    FactorGraph,
    VariableFactory,
    FactorList,
    ScheduleSequence,
    )

from skills.trueskill.layers import (
    IteratedTeamDifferencesInnerLayer,
    IteratedTeamDifferencesInnerLayerError,
    PlayerPerformancesToTeamPerformancesLayer,
    PlayerPriorValuesToSkillsLayer,
    PlayerSkillsToPerformancesLayer,
    TeamDifferencesComparisonLayer,
    TeamPerformancesToTeamPerformanceDifferencesLayer,
    )

from skills.trueskill.truncated import (
    v_exceeds_margin_scaled,
    v_within_margin_scaled,
    w_exceeds_margin_scaled,
    w_within_margin_scaled,
    )


class TrueSkillGameInfo(object):
    '''Parameters about the game used for calculating new skills'''

    DEFAULT_INITIAL_MEAN = 25.0
    DEFAULT_INITIAL_STANDARD_DEVIATION = DEFAULT_INITIAL_MEAN / 3
    DEFAULT_BETA = DEFAULT_INITIAL_MEAN / 6
    DEFAULT_DYNAMICS_FACTOR = DEFAULT_INITIAL_MEAN / 300
    DEFAULT_DRAW_PROBABILITY = 0.10
    DEFAULT_CONSERVATIVE_STANDARD_DEVIATION_MULTIPLIER = 3.0

    def __init__(self, initial_mean=DEFAULT_INITIAL_MEAN,
                       stdev=DEFAULT_INITIAL_STANDARD_DEVIATION,
                       beta=DEFAULT_BETA,
                       dynamics_factor=DEFAULT_DYNAMICS_FACTOR,
                       draw_probability=DEFAULT_DRAW_PROBABILITY,
                       conservative_stdev_multiplier=DEFAULT_CONSERVATIVE_STANDARD_DEVIATION_MULTIPLIER):

        try:
            self.initial_mean = float(initial_mean)
            self.initial_stdev = float(stdev)
            self.beta = float(beta)
            self.dynamics_factor = float(dynamics_factor)
            self.draw_probability = float(draw_probability)
            self.conservative_stdev_multiplier = float(conservative_stdev_multiplier)
            self.draw_margin = float(Gaussian.inverse_cumulative_to(0.5 * (self.draw_probability + 1), 0, 1) *
                                     sqrt(1 + 1) * self.beta)
        except ValueError:
            raise ValueError("TrueSkillGameInfo arguments must be numeric")

    def default_rating(self):
        return GaussianRating(self.initial_mean, self.initial_stdev)

    @staticmethod
    def ensure_game_info(game_info):
        if (not hasattr(game_info, 'initial_mean') or
                not hasattr(game_info, 'initial_stdev') or
                not hasattr(game_info, 'beta') or
                not hasattr(game_info, 'dynamics_factor') or
                not hasattr(game_info, 'draw_probability') or
                not hasattr(game_info, 'conservative_stdev_multiplier') or
                not hasattr(game_info, 'draw_margin')):
            if isinstance(game_info, Sequence):
                try:
                    return TrueSkillGameInfo(*game_info)
                except TypeError:
                    raise TypeError("game_info must be a sequence of length 0 to 6 or a TrueSkillGameInfo object")
            else:
                try:
                    return TrueSkillGameInfo(game_info)
                except TypeError:
                    raise TypeError("game_info was passed the wrong number of arguments")
        else:
            return game_info


class TwoPlayerTrueSkillCalculator(Calculator):
    '''Implements TrueSkill calculations for one-on-one games'''

    score = {WIN: 1.0,
             LOSE:-1.0,
             DRAW: 0.0}

    def __init__(self):
        Calculator.__init__(self, Range.exactly(2), Range.exactly(1))
        RatingFactory.rating_class = GaussianRating

    def new_ratings(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        # ensure sorted by rank
        teams.sort()

        winner, winner_rating = teams[0].player_rating()[0]
        loser, loser_rating = teams[1].player_rating()[0]

        return Match([Team({winner: self.new_rating(winner_rating,
                                                    loser_rating,
                                                    teams.comparison(0, 1),
                                                    game_info)}),
                      Team({loser: self.new_rating(loser_rating,
                                                   winner_rating,
                                                   teams.comparison(1, 0),
                                                   game_info)})])

    def new_rating(self, self_rating, opponent_rating, comparison, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        if comparison == LOSE:
            mean_delta = opponent_rating.mean - self_rating.mean
        else:
            mean_delta = self_rating.mean - opponent_rating.mean

        c = sqrt(
            self_rating.stdev ** 2.0 +
            opponent_rating.stdev ** 2.0 +
            2.0 * game_info.beta ** 2.0
        )

        if comparison != DRAW:
            v = v_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = w_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = TwoPlayerTrueSkillCalculator.score[comparison]
        else:
            v = v_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = w_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0

        mean_multiplier = (self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0) / c

        variance_with_dynamics = self_rating.stdev ** 2.0 + game_info.dynamics_factor ** 2.0
        std_dev_multiplier = variance_with_dynamics / (c ** 2.0)

        new_mean = self_rating.mean + (rank_multiplier * mean_multiplier * v)
        new_std_dev = sqrt(variance_with_dynamics * (1.0 - w * std_dev_multiplier))

        return GaussianRating(new_mean, new_std_dev)

    def match_quality(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        player1rating, player2rating = [team.ratings()[0] for team in teams]

        twice_beta_squared = 2.0 * game_info.beta ** 2.0
        player1sigma_squared = player1rating.stdev ** 2.0
        player2sigma_squared = player2rating.stdev ** 2.0

        sqrt_part = sqrt(
            twice_beta_squared / (twice_beta_squared + player1sigma_squared + player2sigma_squared)
        )

        exp_part = exp(
            (-1.0 * (player1rating.mean - player2rating.mean) ** 2.0) /
            (2.0 * (twice_beta_squared + player1sigma_squared + player2sigma_squared))
        )

        return sqrt_part * exp_part


class TwoTeamTrueSkillCalculator(Calculator):
    '''
    Calculates new ratings for only two teams
    where each team has 1 or more players.
    '''

    score = {WIN: 1.0,
             LOSE:-1.0,
             DRAW: 0.0}

    def __init__(self):
        Calculator.__init__(self, Range.exactly(2), Range.at_least(1))
        RatingFactory.rating_class = GaussianRating

    def new_ratings(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)
        teams.sort()

        return Match([self.new_team_ratings(teams[0], teams[1],
                                            teams.comparison(0, 1), game_info),
                      self.new_team_ratings(teams[1], teams[0],
                                            teams.comparison(1, 0), game_info)])

    def new_team_ratings(self, self_team, other_team,
                         self_to_other_team_comparison, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self_mean_sum = sum(rating.mean for rating in self_team.ratings())
        other_team_mean_sum = sum(rating.mean for rating in other_team.ratings())
        if self_to_other_team_comparison == LOSE:
            mean_delta = other_team_mean_sum - self_mean_sum
        else:
            mean_delta = self_mean_sum - other_team_mean_sum

        c = sqrt(
            sum(rating.stdev ** 2.0 for rating in self_team.ratings()) +
            sum(rating.stdev ** 2.0 for rating in other_team.ratings()) +
            (len(self_team) + len(other_team)) * game_info.beta ** 2
        )
        tau_squared = game_info.dynamics_factor ** 2

        if self_to_other_team_comparison != DRAW:
            v = v_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = w_exceeds_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = TwoTeamTrueSkillCalculator.score[self_to_other_team_comparison]
        else:
            v = v_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            w = w_within_margin_scaled(mean_delta, game_info.draw_margin, c)
            rank_multiplier = 1.0

        new_team_ratings = Team()

        for self_team_current_player, previous_player_rating in self_team.player_rating():
            mean_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / c
            std_dev_multiplier = (previous_player_rating.stdev ** 2.0 + tau_squared) / (c ** 2.0)

            player_mean_delta = rank_multiplier * mean_multiplier * v
            new_mean = previous_player_rating.mean + player_mean_delta

            new_std_dev = sqrt(
                (previous_player_rating.stdev ** 2.0 + tau_squared) * (1.0 - w * std_dev_multiplier)
            )

            new_team_ratings[self_team_current_player] = GaussianRating(new_mean, new_std_dev)

        return new_team_ratings

    def match_quality(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        team1ratings = teams[0].ratings()
        team2ratings = teams[1].ratings()

        total_players = sum(len(team) for team in teams)

        beta_squared = game_info.beta ** 2.0

        team1mean_sum = sum(player.mean for player in team1ratings)
        team1stdev_squared = sum(player.stdev ** 2.0 for player in team1ratings)

        team2mean_sum = sum(player.mean for player in team2ratings)
        team2stdev_squared = sum(player.stdev ** 2.0 for player in team2ratings)

        sqrt_part = sqrt(
            (total_players * beta_squared) /
            (total_players * beta_squared + team1stdev_squared +
                                            team2stdev_squared)
        )

        exp_part = exp(
            (-1.0 * (team1mean_sum - team2mean_sum) ** 2.0) /
            (2.0 * (total_players * beta_squared + team1stdev_squared +
                                                   team2stdev_squared))
        )

        return exp_part * sqrt_part


class TrueSkillFactorGraph(FactorGraph):

    def __init__(self, teams, team_ranks, game_info):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        FactorGraph.__init__(self)
        self.prior_layer = PlayerPriorValuesToSkillsLayer(self, teams)
        self.game_info = game_info
        new_factory = VariableFactory(lambda: Gaussian.from_precision_mean(0.0, 0.0))
        self.variable_factory = new_factory
        self.layers = [
            self.prior_layer,
            PlayerSkillsToPerformancesLayer(self),
            PlayerPerformancesToTeamPerformancesLayer(self),
            IteratedTeamDifferencesInnerLayer(self,
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


class FactorGraphTrueSkillCalculator(Calculator):
    '''
    Calculates TrueSkill using a full factor graph.
    '''

    def __init__(self):
        Calculator.__init__(self, Range.at_least(2), Range.at_least(1), True, True)
        RatingFactory.rating_class = GaussianRating

    def new_ratings(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
        self.validate_team_and_player_counts(teams)

        # ensure sorted by rank
        teams.sort()

        factor_graph = TrueSkillFactorGraph(teams, teams.rank, game_info)
        factor_graph.build_graph()
        factor_graph.run_schedule()

        #probability_of_outcome = factor_graph.probability_of_ranking()

        return factor_graph.updated_ratings()

    def match_quality(self, teams, game_info=None):
        game_info = TrueSkillGameInfo.ensure_game_info(game_info)
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
                player_assignments[current_column].append(current_player.partial_play_percentage)
                total_previous_players += 1
            rows_remaining = total_players - total_previous_players
            next_team = teams[current_column + 1]
            for next_team_player in next_team.players():
                player_assignments[current_column].append(-1.0 * next_team_player.partial_play_percentage)
                rows_remaining -= 1
            player_assignments[current_column].extend([0.0] * rows_remaining)

        return Matrix(player_assignments).transpose()
