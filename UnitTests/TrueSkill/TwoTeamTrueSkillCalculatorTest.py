import unittest
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TrueSkillCalculatorTests
from Skills.TrueSkill.TwoTeamTrueSkillCalculator import TwoTeamTrueSkillCalculator

class TwoTeamTrueSkillCalculatorTest(TrueSkillCalculatorTests):

    def testTwoTeamTrueSkillCalculator(self):
        calculator = TwoTeamTrueSkillCalculator()

        self.allTwoPlayerScenarios(calculator)
        self.allTwoTeamScenarios(calculator)

if __name__ == "__main__":
    unittest.main()
