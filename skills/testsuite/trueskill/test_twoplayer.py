import unittest
from skills.testsuite.trueskill import TwoPlayerCalculatorTests
from skills.trueskill import TwoPlayerTrueSkillCalculator


class TwoPlayerTrueSkillCalculatorTest(unittest.TestCase, TwoPlayerCalculatorTests):

    def setUp(self):
        self.calculator = TwoPlayerTrueSkillCalculator()


if __name__ == "__main__":
    unittest.main()
