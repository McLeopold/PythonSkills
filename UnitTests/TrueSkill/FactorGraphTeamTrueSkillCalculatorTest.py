import unittest
from Skills.TrueSkill.FactorGraphTrueSkillCalculator import FactorGraphTrueSkillCalculator
from UnitTests.TrueSkill.TrueSkillCalculatorTests import TwoPlayerCalculatorTests, TwoTeamCalculatorTests, MultipleTeamCalculatorTests, PartialPlayCalculatorTests
import logging
from Skills.FactorGraphs.Schedule import Schedule

class FactorGraphTeamTrueSkillCalculatorTest(unittest.TestCase,
                                             TwoPlayerCalculatorTests,
                                             TwoTeamCalculatorTests,
                                             MultipleTeamCalculatorTests,
                                             PartialPlayCalculatorTests):


    def setUp(self):
        self.calculator = FactorGraphTrueSkillCalculator()
        if False:
            # setup console stderr logging for all tests
            log = logging.getLogger("calc")
            log.addHandler(logging.StreamHandler())
            log.setLevel(logging.INFO)
            # modify base schedule object to use logging
            Schedule.log = log.info

if __name__ == "__main__":
    unittest.main()
