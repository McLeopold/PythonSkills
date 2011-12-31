import unittest
from Skills.TrueSkill.TwoPlayerTrueSkillCalculator import TwoPlayerTrueSkillCalculator
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TrueSkillCalculatorTests

class TwoPlayerTrueSkillCalculatorTest(TrueSkillCalculatorTests):

    def testTwoPlayerTrueSkillCalculator(self):
        calculator = TwoPlayerTrueSkillCalculator()
        
        self.allTwoPlayerScenarios(calculator)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TwoPlayerTrueSkillCalculatorTest .testTwoPlayerTrueSkillCalculator']
    unittest.main()