from __future__ import division
import unittest
from skills.numerics import Gaussian
from math import sqrt


class GaussianDistributionTest(unittest.TestCase):

    ERROR_TOLERANCE = 0.000000000000002

    def testCumulativeTo(self):
        expected = 0.691462461274013
        answer = Gaussian.cumulative_to(0.5)
        self.assertAlmostEqual(expected, answer, None,
                               "testCumulativeTo expected %.15f, got %.15f" % (expected, answer),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testAt(self):
        expected = 0.352065326764300
        answer = Gaussian.at(0.5)
        self.assertAlmostEqual(expected, answer, None,
                               "testAt expected %.15f, got %.15f" % (expected, answer),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testMultiplication(self):
        standard_normal = Gaussian(0, 1)
        shifted_gaussian = Gaussian(2, 3)
        product = standard_normal * shifted_gaussian

        self.assertAlmostEqual(0.2, product.mean, None,
                               "testMultiplication mean expected %.15f, got %.15f" % (0.2, product.mean),
                               GaussianDistributionTest.ERROR_TOLERANCE)
        self.assertAlmostEqual(3.0 / sqrt(10), product.stdev, None,
                               "testMultiplication stdev expected %.15f, got %.15f" % (0.2, product.mean),
                               GaussianDistributionTest.ERROR_TOLERANCE)

        m4s5 = Gaussian(4, 5)
        m6s7 = Gaussian(6, 7)
        product2 = m4s5 * m6s7

        expectedMean = (4.0 * 7.0 ** 2 + 6.0 * 5.0 ** 2) / (5.0 ** 2 + 7.0 ** 2)
        self.assertAlmostEqual(expectedMean, product2.mean, None,
                               "testMultiplication mean2 expected %.15f, got %.15f" % (expectedMean, product2.mean),
                               GaussianDistributionTest.ERROR_TOLERANCE)

        expectedSigma = sqrt((5.0 ** 2 * 7.0 ** 2) / (5.0 ** 2 + 7.0 ** 2))
        self.assertAlmostEqual(expectedSigma, product2.stdev, None,
                               "testMultiplication stdev2 expected %.15f, got %.15f" % (expectedSigma, product2.stdev),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testDivision(self):
        product = Gaussian(0.2, 3.0 / sqrt(10))
        standard_normal = Gaussian(0.0, 1.0)

        product_divided_by_standard_normal = product / standard_normal
        self.assertAlmostEqual(2.0, product_divided_by_standard_normal.mean, None,
                               "testDivision mean expected %.15f, got %.15f" % (2.0, product_divided_by_standard_normal.mean),
                               GaussianDistributionTest.ERROR_TOLERANCE)
        self.assertAlmostEqual(3.0, product_divided_by_standard_normal.stdev, None,
                               "testDivision stdev expected %.15f, got %.15f" % (3.0, product_divided_by_standard_normal.stdev),
                               GaussianDistributionTest.ERROR_TOLERANCE)

        product2 = Gaussian((4.0 * 7.0 ** 2 + 6.0 * 5.0 ** 2) / (5.0 ** 2 + 7.0 ** 2), sqrt((5.0 ** 2 * 7.0 ** 2) / (5.0 ** 2 + 7.0 ** 2)))
        m4s5 = Gaussian(4.0, 5.0)
        product2divided_by_m4s5 = product2 / m4s5
        self.assertAlmostEqual(6.0, product2divided_by_m4s5.mean, None,
                               "testDivision mean2 expected %.15f, got %.15f" % (6.0, product2divided_by_m4s5.mean),
                               GaussianDistributionTest.ERROR_TOLERANCE)
        self.assertAlmostEqual(7.0, product2divided_by_m4s5.stdev, None,
                               "testDivision stdev2 expected %.15f, got %.15f" % (7.0, product2divided_by_m4s5.stdev),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testLogProductNormalization(self):
        standard_normal = Gaussian(0, 1)
        lpn = Gaussian.log_product_normalization(standard_normal, standard_normal)
        answer = -1.2655121234846454
        self.assertAlmostEqual(answer, lpn, None,
                               "testLogProductNormalization lpn expected %.15f, got %.15f" % (answer, lpn),
                               GaussianDistributionTest.ERROR_TOLERANCE)

        m1s2 = Gaussian(1.0, 2.0)
        m3s4 = Gaussian(3.0, 4.0)
        lpn2 = Gaussian.log_product_normalization(m1s2, m3s4)
        answer = -2.5168046699816684
        self.assertAlmostEqual(answer, lpn2, None,
                               "testLogProductNormalization lpn2 expected %.15f, got %.15f" % (answer, lpn2),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testLogRatioNormalization(self):
        m1s2 = Gaussian(1.0, 2.0)
        m3s4 = Gaussian(3.0, 4.0)
        lrn = Gaussian.log_ratio_normalization(m1s2, m3s4)
        answer = 2.6157405972171204
        self.assertAlmostEqual(answer, lrn, None,
                               "testLogRatioNormalization lrn expected %.15f, got %.15f" % (answer, lrn),
                               GaussianDistributionTest.ERROR_TOLERANCE)

    def testSubtraction(self):
        standard_normal = Gaussian(0.0, 1.0)
        abs_diff = standard_normal - standard_normal
        self.assertAlmostEqual(0.0, abs_diff, None,
                               "testAbsoluteDifference abs_diff expected %.15f, got %.15f" % (0.0, abs_diff),
                               GaussianDistributionTest.ERROR_TOLERANCE)

        m1s2 = Gaussian(1.0, 2.0)
        m3s4 = Gaussian(3.0, 4.0)
        abs_diff2 = m1s2 - m3s4
        answer = 0.4330127018922193
        self.assertAlmostEqual(0.0, abs_diff, None,
                               "testAbsoluteDifference abs_diff2 expected %.15f, got %.15f" % (answer, abs_diff2),
                               GaussianDistributionTest.ERROR_TOLERANCE)


if __name__ == "__main__":
    unittest.main()
