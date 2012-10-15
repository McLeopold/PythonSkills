from skills import (
    Match,
    )

from skills.trueskill import TrueSkillGameInfo

from skills.numerics import Matrix


class CalculatorTests(object):

    ERROR_TOLERANCE_TRUESKILL = 0.085
    ERROR_TOLERANCE_MATCH_QUALITY = 0.0005

    def __init__(self):
        self.calculator = None

    def assertAlmostEqual(self, first, second, places, msg, delta):
        raise NotImplementedError

    def assertRating(self, expected_mean, expected_stdev, actual):
        self.assertAlmostEqual(expected_mean, actual.mean, None,
                               "expected mean of %.14f, got %.14f" % (expected_mean, actual.mean),
                               CalculatorTests.ERROR_TOLERANCE_TRUESKILL)
        self.assertAlmostEqual(expected_stdev, actual.stdev, None,
                               "expected standard deviation of %.14f, got %.14f" % (expected_stdev, actual.stdev),
                               CalculatorTests.ERROR_TOLERANCE_TRUESKILL)

    def assertMatchQuality(self, expected_match_quality, actual_match_quality):
        #self.assertEqual(expected_match_quality, actual_match_quality, "expected match quality of %f, got %f" % (expected_match_quality, actual_match_quality))
        self.assertAlmostEqual(expected_match_quality, actual_match_quality, None,
                               "expected match quality of %.15f, got %.15f" % (expected_match_quality, actual_match_quality),
                               CalculatorTests.ERROR_TOLERANCE_MATCH_QUALITY)


class TwoPlayerCalculatorTests(CalculatorTests):

    def test_two_player_not_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)}],
                      [1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.447214, self.calculator.match_quality(teams, game_info))
        self.assertRating(29.39583201999924, 7.171475587326186, new_ratings.rating_by_id(1))
        self.assertRating(20.60416798000076, 7.171475587326186, new_ratings.rating_by_id(2))

    def test_two_player_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.447, self.calculator.match_quality(teams, game_info))
        self.assertRating(25.0, 6.4575196623173081, new_ratings.rating_by_id(1))
        self.assertRating(25.0, 6.4575196623173081, new_ratings.rating_by_id(2))

    def test_two_player_chess_not_drawn(self):
        game_info = TrueSkillGameInfo(1200.0, 1200.0 / 3, 200.0, 1200.0 / 300, 0.03)
        teams = Match([{1: (1301.0007, 42.9232)},
                       {2: (1188.7560, 42.5570)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertRating(1304.7820836053318, 42.843513887848658, new_ratings.rating_by_id(1))
        self.assertRating(1185.0383099003536, 42.485604606897752, new_ratings.rating_by_id(2))

    def test_one_on_one_massive_upset_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (50.0, 25.0 / 2)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.110, self.calculator.match_quality(teams, game_info))
        self.assertRating(31.662, 7.137, new_ratings.rating_by_id(1))
        self.assertRating(35.010, 7.910, new_ratings.rating_by_id(2))


class TwoTeamCalculatorTests(CalculatorTests):

    def test_two_on_two(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3),
                        2: (25.0, 25.0 / 3)},

                       {3: (25.0, 25.0 / 3),
                        4: (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.447, self.calculator.match_quality(teams, game_info))
        self.assertRating(28.108, 7.774, new_ratings.rating_by_id(1))
        self.assertRating(28.108, 7.774, new_ratings.rating_by_id(2))
        self.assertRating(21.892, 7.774, new_ratings.rating_by_id(3))
        self.assertRating(21.892, 7.774, new_ratings.rating_by_id(4))

    def test_two_on_two_draw(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3),
                        2: (25.0, 25.0 / 3)},

                       {3: (25.0, 25.0 / 3),
                        4: (25.0, 25.0 / 3)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.447, self.calculator.match_quality(teams, game_info))
        self.assertRating(25.0, 7.455, new_ratings.rating_by_id(1))
        self.assertRating(25.0, 7.455, new_ratings.rating_by_id(2))
        self.assertRating(25.0, 7.455, new_ratings.rating_by_id(3))
        self.assertRating(25.0, 7.455, new_ratings.rating_by_id(4))

    def test_two_on_two_unbalanced_draw(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (15.0, 8.0),
                        2: (20.0, 6.0)},

                       {3: (25.0, 4.0),
                        4: (30.0, 3.0)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.214, self.calculator.match_quality(teams, game_info))
        self.assertRating(21.570, 6.556, new_ratings.rating_by_id(1))
        self.assertRating(23.696, 5.418, new_ratings.rating_by_id(2))
        self.assertRating(23.357, 3.833, new_ratings.rating_by_id(3))
        self.assertRating(29.075, 2.931, new_ratings.rating_by_id(4))

    def test_two_on_two_upset(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (20.0, 8.0),
                        2: (25.0, 6.0)},

                       {3: (35.0, 7.0),
                        4: (40.0, 5.0)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.084, self.calculator.match_quality(teams, game_info))
        self.assertRating(29.698, 7.008, new_ratings.rating_by_id(1))
        self.assertRating(30.455, 5.594, new_ratings.rating_by_id(2))
        self.assertRating(27.575, 6.346, new_ratings.rating_by_id(3))
        self.assertRating(36.211, 4.768, new_ratings.rating_by_id(4))

    def test_four_on_four(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3),
                        2: (25.0, 25.0 / 3),
                        3: (25.0, 25.0 / 3),
                        4: (25.0, 25.0 / 3)},

                       {5: (25.0, 25.0 / 3),
                        6: (25.0, 25.0 / 3),
                        7: (25.0, 25.0 / 3),
                        8: (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.447, self.calculator.match_quality(teams, game_info))
        self.assertRating(27.198, 8.059, new_ratings.rating_by_id(1))
        self.assertRating(27.198, 8.059, new_ratings.rating_by_id(2))
        self.assertRating(27.198, 8.059, new_ratings.rating_by_id(3))
        self.assertRating(27.198, 8.059, new_ratings.rating_by_id(4))
        self.assertRating(22.802, 8.059, new_ratings.rating_by_id(5))
        self.assertRating(22.802, 8.059, new_ratings.rating_by_id(6))
        self.assertRating(22.802, 8.059, new_ratings.rating_by_id(7))
        self.assertRating(22.802, 8.059, new_ratings.rating_by_id(8))

    def test_one_on_two(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3), 3: (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.135, self.calculator.match_quality(teams, game_info))
        self.assertRating(33.730, 7.317, new_ratings.rating_by_id(1))
        self.assertRating(16.270, 7.317, new_ratings.rating_by_id(2))
        self.assertRating(16.270, 7.317, new_ratings.rating_by_id(3))

    def test_one_on_two_somewhat_balanced(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (40.0, 6.0)},
                       {2: (20.0, 7.0), 3: (25.0, 8.0)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.478, self.calculator.match_quality(teams, game_info))
        self.assertRating(42.744, 5.602, new_ratings.rating_by_id(1))
        self.assertRating(16.266, 6.359, new_ratings.rating_by_id(2))
        self.assertRating(20.123, 7.028, new_ratings.rating_by_id(3))

    def test_one_on_three(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3), 3: (25.0, 25.0 / 3), 4: (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.012, self.calculator.match_quality(teams, game_info))
        self.assertRating(36.337, 7.527, new_ratings.rating_by_id(1))
        self.assertRating(13.663, 7.527, new_ratings.rating_by_id(2))
        self.assertRating(13.663, 7.527, new_ratings.rating_by_id(3))
        self.assertRating(13.663, 7.527, new_ratings.rating_by_id(4))

    def test_one_on_two_draw(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3), 3: (25.0, 25.0 / 3)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.135, self.calculator.match_quality(teams, game_info))
        self.assertRating(31.660, 7.138, new_ratings.rating_by_id(1))
        self.assertRating(18.340, 7.138, new_ratings.rating_by_id(2))
        self.assertRating(18.340, 7.138, new_ratings.rating_by_id(3))

    def test_one_on_three_draw(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3), 3: (25.0, 25.0 / 3), 4: (25.0, 25.0 / 3)}],
                      rank=[1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.012, self.calculator.match_quality(teams, game_info))
        self.assertRating(34.990, 7.455, new_ratings.rating_by_id(1))
        self.assertRating(15.010, 7.455, new_ratings.rating_by_id(2))
        self.assertRating(15.010, 7.455, new_ratings.rating_by_id(3))
        self.assertRating(15.010, 7.455, new_ratings.rating_by_id(4))

    def test_one_on_seven(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3),
                        3: (25.0, 25.0 / 3),
                        4: (25.0, 25.0 / 3),
                        5: (25.0, 25.0 / 3),
                        6: (25.0, 25.0 / 3),
                        7: (25.0, 25.0 / 3),
                        8: (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.000, self.calculator.match_quality(teams, game_info))
        self.assertRating(40.582, 7.917, new_ratings.rating_by_id(1))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(2))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(3))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(4))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(5))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(6))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(7))
        self.assertRating(9.418, 7.917, new_ratings.rating_by_id(8))

    def test_three_on_two(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (28.0, 7.0), 2: (27.0, 6.0), 3: (26.0, 5.0)},
                       {4: (30.0, 4.0), 5: (31.0, 3.0)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.254, self.calculator.match_quality(teams, game_info))
        self.assertRating(28.658, 6.770, new_ratings.rating_by_id(1))
        self.assertRating(27.484, 5.856, new_ratings.rating_by_id(2))
        self.assertRating(26.336, 4.917, new_ratings.rating_by_id(3))
        self.assertRating(29.785, 3.958, new_ratings.rating_by_id(4))
        self.assertRating(30.879, 2.983, new_ratings.rating_by_id(5))


class MultipleTeamCalculatorTests(CalculatorTests):

    def test_two_on_four_on_two_win_draw(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (40.0, 4.0),
                        2: (45.0, 3.0)},

                       {3: (20.0, 7.0),
                        4: (19.0, 6.0),
                        5: (30.0, 9.0),
                        6: (10.0, 4.0)},

                       {7: (50.0, 5.0),
                        8: (30.0, 2.0)}],
                      rank=[1, 2, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.367, self.calculator.match_quality(teams, game_info))
        self.assertRating(40.877, 3.840, new_ratings.rating_by_id(1))
        self.assertRating(45.493, 2.934, new_ratings.rating_by_id(2))
        self.assertRating(19.609, 6.396, new_ratings.rating_by_id(3))
        self.assertRating(18.712, 5.625, new_ratings.rating_by_id(4))
        self.assertRating(29.353, 7.673, new_ratings.rating_by_id(5))
        self.assertRating(9.872, 3.891, new_ratings.rating_by_id(6))
        self.assertRating(48.830, 4.590, new_ratings.rating_by_id(7))
        self.assertRating(29.813, 1.976, new_ratings.rating_by_id(8))

    def test_three_teams_of_one_not_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)}],
                      rank=[1, 2, 3])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.200, self.calculator.match_quality(teams, game_info))
        self.assertRating(31.675352419172107, 6.6559853776206905, new_ratings.rating_by_id(1))
        self.assertRating(25.000000000003912, 6.2078966412243233, new_ratings.rating_by_id(2))
        self.assertRating(18.324647580823971, 6.6559853776218318, new_ratings.rating_by_id(3))

    def test_three_teams_of_one_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)}],
                      rank=[1, 1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.200, self.calculator.match_quality(teams, game_info))
        self.assertRating(25.0, 5.698, new_ratings.rating_by_id(1))
        self.assertRating(25.0, 5.695, new_ratings.rating_by_id(2))
        self.assertRating(25.0, 5.698, new_ratings.rating_by_id(3))

    def test_four_teams_of_one_not_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)},
                       {4: (25.0, 25.0 / 3)}],
                      rank=[1, 2, 3, 4])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.089, self.calculator.match_quality(teams, game_info))
        self.assertRating(33.206680965631264, 6.3481091698077057, new_ratings.rating_by_id(1))
        self.assertRating(27.401454693843323, 5.7871629348447584, new_ratings.rating_by_id(2))
        self.assertRating(22.598545306188374, 5.7871629348413451, new_ratings.rating_by_id(3))
        self.assertRating(16.793319034361271, 6.3481091698144967, new_ratings.rating_by_id(4))

    def test_five_teams_of_one_not_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)},
                       {4: (25.0, 25.0 / 3)},
                       {5: (25.0, 25.0 / 3)}],
                      rank=[1, 2, 3, 4, 5])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.040, self.calculator.match_quality(teams, game_info))
        self.assertRating(34.363135705841188, 6.1361528798112692, new_ratings.rating_by_id(1))
        self.assertRating(29.058448805636779, 5.5358352402833413, new_ratings.rating_by_id(2))
        self.assertRating(25.000000000031758, 5.4200805474429847, new_ratings.rating_by_id(3))
        self.assertRating(20.941551194426314, 5.5358352402709672, new_ratings.rating_by_id(4))
        self.assertRating(15.636864294158848, 6.136152879829349, new_ratings.rating_by_id(5))

    def test_eight_teams_of_one_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)},
                       {4: (25.0, 25.0 / 3)},
                       {5: (25.0, 25.0 / 3)},
                       {6: (25.0, 25.0 / 3)},
                       {7: (25.0, 25.0 / 3)},
                       {8: (25.0, 25.0 / 3)}],
                      rank=[1, 1, 1, 1, 1, 1, 1, 1])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.004, self.calculator.match_quality(teams, game_info))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(1))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(2))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(3))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(4))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(5))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(6))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(7))
        self.assertRating(25.000, 4.592, new_ratings.rating_by_id(8))

    def test_eight_teams_of_one_upset(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (10.0, 8.0)},
                       {2: (15.0, 7.0)},
                       {3: (20.0, 6.0)},
                       {4: (25.0, 5.0)},
                       {5: (30.0, 4.0)},
                       {6: (35.0, 3.0)},
                       {7: (40.0, 2.0)},
                       {8: (45.0, 1.0)}],
                      rank=[1, 2, 3, 4, 5, 6, 7, 8])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.000, self.calculator.match_quality(teams, game_info))
        self.assertRating(35.135, 4.506, new_ratings.rating_by_id(1))
        self.assertRating(32.585, 4.037, new_ratings.rating_by_id(2))
        self.assertRating(31.329, 3.756, new_ratings.rating_by_id(3))
        self.assertRating(30.984, 3.453, new_ratings.rating_by_id(4))
        self.assertRating(31.751, 3.064, new_ratings.rating_by_id(5))
        self.assertRating(34.051, 2.541, new_ratings.rating_by_id(6))
        self.assertRating(38.263, 1.849, new_ratings.rating_by_id(7))
        self.assertRating(44.118, 0.983, new_ratings.rating_by_id(8))

    def test_sixteen_teams_of_one_not_drawn(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {2: (25.0, 25.0 / 3)},
                       {3: (25.0, 25.0 / 3)},
                       {4: (25.0, 25.0 / 3)},
                       {5: (25.0, 25.0 / 3)},
                       {6: (25.0, 25.0 / 3)},
                       {7: (25.0, 25.0 / 3)},
                       {8: (25.0, 25.0 / 3)},
                       {9: (25.0, 25.0 / 3)},
                       {10: (25.0, 25.0 / 3)},
                       {11: (25.0, 25.0 / 3)},
                       {12: (25.0, 25.0 / 3)},
                       {13: (25.0, 25.0 / 3)},
                       {14: (25.0, 25.0 / 3)},
                       {15: (25.0, 25.0 / 3)},
                       {16: (25.0, 25.0 / 3)}],
                      rank=list(range(16)))
        new_ratings = self.calculator.new_ratings(teams, game_info)
        # naive matrix implementation too slow with 16 teams
        if not hasattr(Matrix, 'is_square'):
            self.assertMatchQuality(0.000, self.calculator.match_quality(teams, game_info))
        self.assertRating(40.53945776946920, 5.27581643889050, new_ratings.rating_by_id(1))
        self.assertRating(36.80951229454210, 4.71121217610266, new_ratings.rating_by_id(2))
        self.assertRating(34.34726355544460, 4.52440328139991, new_ratings.rating_by_id(3))
        self.assertRating(32.33614722608720, 4.43258628279632, new_ratings.rating_by_id(4))
        self.assertRating(30.55048814671730, 4.38010805034365, new_ratings.rating_by_id(5))
        self.assertRating(28.89277312234790, 4.34859291776483, new_ratings.rating_by_id(6))
        self.assertRating(27.30952161972210, 4.33037679041216, new_ratings.rating_by_id(7))
        self.assertRating(25.76571046519540, 4.32197078088701, new_ratings.rating_by_id(8))
        self.assertRating(24.23428953480470, 4.32197078088703, new_ratings.rating_by_id(9))
        self.assertRating(22.69047838027800, 4.33037679041219, new_ratings.rating_by_id(10))
        self.assertRating(21.10722687765220, 4.34859291776488, new_ratings.rating_by_id(11))
        self.assertRating(19.44951185328290, 4.38010805034375, new_ratings.rating_by_id(12))
        self.assertRating(17.66385277391300, 4.43258628279643, new_ratings.rating_by_id(13))
        self.assertRating(15.65273644455550, 4.52440328139996, new_ratings.rating_by_id(14))
        self.assertRating(13.19048770545810, 4.71121217610273, new_ratings.rating_by_id(15))
        self.assertRating(9.46054223053080, 5.27581643889032, new_ratings.rating_by_id(16))


class PartialPlayCalculatorTests(CalculatorTests):

    def test_one_on_two_balanced_partial_play(self):
        game_info = TrueSkillGameInfo()
        teams = Match([{1: (25.0, 25.0 / 3)},
                       {(2, 0.5): (25.0, 25.0 / 3),
                        (3, 0.5): (25.0, 25.0 / 3)}],
                      rank=[1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.4472135955, self.calculator.match_quality(teams, game_info))
        self.assertRating(30.1102397877, 6.73461146087, new_ratings.rating_by_id(1))
        self.assertRating(22.4448801061, 7.96412515904, new_ratings.rating_by_id(2))
        self.assertRating(22.4448801061, 7.96412515904, new_ratings.rating_by_id(3))
