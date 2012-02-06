import unittest
from skills.trueskill import TwoTeamTrueSkillCalculator

from tests.trueskill import (
    TwoPlayerCalculatorTests,
    TwoTeamCalculatorTests,
    )


class TwoTeamTrueSkillCalculatorTest(unittest.TestCase, TwoPlayerCalculatorTests, TwoTeamCalculatorTests):

    def setUp(self):
        self.calculator = TwoTeamTrueSkillCalculator()


if __name__ == "__main__":
    unittest.main()
