import unittest
from Skills.TrueSkill.TwoTeamTrueSkillCalculator import TwoTeamTrueSkillCalculator
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TwoPlayerCalculatorTests, TwoTeamCalculatorTests

class TwoTeamTrueSkillCalculatorTest(unittest.TestCase, TwoPlayerCalculatorTests, TwoTeamCalculatorTests):

    def setUp(self):
        self.calculator = TwoTeamTrueSkillCalculator()

if __name__ == "__main__":
    unittest.main()
