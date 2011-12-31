import unittest
from Skills.TrueSkill.FactorGraphTrueSkillCalculator import FactorGraphTrueSkillCalculator
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TrueSkillCalculatorTests
import logging
from Skills.FactorGraphs.Schedule import Schedule

class FactorGraphTeamTrueSkillCalculatorTest(TrueSkillCalculatorTests):

    # setup console stderr logging for all tests
    log = logging.getLogger("calc")
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.INFO)
    # modify base schedule object to use logging
    Schedule.log = log.info

    def testFactorGraphTrueSkillCalculator(self):
        calculator = FactorGraphTrueSkillCalculator()
        
        self.allTwoPlayerScenarios(calculator)
        self.allTwoTeamScenarios(calculator)
        self.allMultipleTeamScenarios(calculator)
        
        self.partialPlayScenarios(calculator)

if __name__ == "__main__":
    unittest.main()
