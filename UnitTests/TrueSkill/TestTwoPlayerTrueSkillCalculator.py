import unittest
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TwoPlayerCalculatorTests
from Skills.TrueSkill.TwoPlayerTrueSkillCalculator import TwoPlayerTrueSkillCalculator

class TwoTeamTrueSkillCalculatorTest(unittest.TestCase, TwoPlayerCalculatorTests):

    def setUp(self):
        self.calculator = TwoPlayerTrueSkillCalculator()

if __name__ == "__main__":
    unittest.main()
