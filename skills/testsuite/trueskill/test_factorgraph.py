import unittest

from skills.trueskill import FactorGraphTrueSkillCalculator

from skills.testsuite.trueskill import (
    TwoPlayerCalculatorTests,
    TwoTeamCalculatorTests,
    MultipleTeamCalculatorTests,
    PartialPlayCalculatorTests,
    )


class FactorGraphTrueSkillCalculatorTest(unittest.TestCase,
                                         TwoPlayerCalculatorTests,
                                         TwoTeamCalculatorTests,
                                         MultipleTeamCalculatorTests,
                                         PartialPlayCalculatorTests):

    def setUp(self):
        self.calculator = FactorGraphTrueSkillCalculator()


if __name__ == "__main__":
    unittest.main()
