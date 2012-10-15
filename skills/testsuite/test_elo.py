import unittest

from skills import (
    Match,
    )

from skills.elo import (
  EloCalculator,
  EloGameInfo
  )


class CalculatorTests(object):

    ERROR_TOLERANCE_RATING = 0.085
    ERROR_TOLERANCE_MATCH_QUALITY = 0.0005

    def assertAlmostEqual(self, first, second, places, msg, delta):
        raise NotImplementedError

    def assertRating(self, expected_mean, actual):
        self.assertAlmostEqual(expected_mean, actual.mean, None,
                               "expected mean of %.14f, got %.14f" % (expected_mean, actual.mean),
                               CalculatorTests.ERROR_TOLERANCE_RATING)

    def assertMatchQuality(self, expected_match_quality, actual_match_quality):
        #self.assertEqual(expected_match_quality, actual_match_quality, "expected match quality of %f, got %f" % (expected_match_quality, actual_match_quality))
        self.assertAlmostEqual(expected_match_quality, actual_match_quality, None,
                               "expected match quality of %.15f, got %.15f" % (expected_match_quality, actual_match_quality),
                               CalculatorTests.ERROR_TOLERANCE_MATCH_QUALITY)


class EloTests(unittest.TestCase, CalculatorTests):

    def setUp(self):
        self.calculator = EloCalculator()

    def test_one_on_one(self):
        game_info = EloGameInfo(1200, 200)
        teams = Match([{1: (1200, 25)},
                       {2: (1400, 25)}],
                      [1, 2])
        new_ratings = self.calculator.new_ratings(teams, game_info)
        self.assertMatchQuality(0.4805, self.calculator.match_quality(teams, game_info))
        self.assertRating(1218.99, new_ratings.rating_by_id(1))
        self.assertRating(1381.01, new_ratings.rating_by_id(2))


if __name__ == "__main__":
    unittest.main()
