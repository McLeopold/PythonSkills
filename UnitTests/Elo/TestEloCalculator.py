import unittest
from Skills.GameInfo import GameInfo
from Skills.Elo.EloCalculator import EloCalculator
from Skills.Teams import Teams
from Skills.Rating import RatingFactory
from Skills.Elo.EloRating import EloRating

class CalculatorTests():

    ERROR_TOLERANCE_TRUESKILL = 0.085
    ERROR_TOLERANCE_MATCH_QUALITY = 0.0005

    def assertRating(self, expected_mean, actual):
        self.assertAlmostEqual(expected_mean, actual.mean, None,
                               "expected mean of %.14f, got %.14f" % (expected_mean, actual.mean),
                               CalculatorTests.ERROR_TOLERANCE_TRUESKILL)

    def assertMatchQuality(self, expected_match_quality, actual_match_quality):
        #self.assertEqual(expected_match_quality, actual_match_quality, "expected match quality of %f, got %f" % (expected_match_quality, actual_match_quality))
        self.assertAlmostEqual(expected_match_quality, actual_match_quality, None,
                               "expected match quality of %.15f, got %.15f" % (expected_match_quality, actual_match_quality),
                               CalculatorTests.ERROR_TOLERANCE_MATCH_QUALITY)

class EloTests(unittest.TestCase, CalculatorTests):

    def setUp(self):
        RatingFactory.rating_class = EloRating
        self.calculator = EloCalculator()

    def test_one_on_one(self):
        game_info = GameInfo()
        teams = Teams.FreeForAll((1, 1200),
                                 (2, 1200),
                                 rank=[1, 2])
        new_ratings = self.calculator.calculate_new_ratings(game_info, teams)

        self.assertMatchQuality(1.0, self.calculator.calculate_match_quality(game_info, teams))

        self.assertRating(1216.0, new_ratings.rating_by_id(1))
        self.assertRating(1184.0, new_ratings.rating_by_id(2))

if __name__ == "__main__":
    unittest.main()
