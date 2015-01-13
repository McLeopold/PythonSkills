from __future__ import division, absolute_import
from math import sqrt, pi, log, exp

try:
    from numpy import matrix as Matrix, linalg
    Matrix.determinant = lambda m: linalg.det(m)
    Matrix.inverse = lambda m: m.I
except ImportError:
    from .matrix import Matrix


SQRT_2_PI = sqrt(2.0 * pi)
LOG_SQRT_2_PI = log(sqrt(2.0 * pi))
INV_SQRT_2 = -1.0 / sqrt(2.0)


class Vector(Matrix):

    def __init__(self, values):
        Matrix.__init__(self, [[value] for value in values])


def DiagonalMatrix(values):
    rows = cols = len(values)
    data = []
    for row in range(rows):
        data.append([0] * cols)
        data[row][row] = values[row]
    return Matrix(data)


def IdentityMatrix(rows):
    return DiagonalMatrix([1] * rows)


class Range(object):

    def __init__(self, minimum, maximum):
        if minimum > maximum:
            raise ValueError("Range minimum > maximum")

        self.minimum = minimum
        self.maximum = maximum

    def __repr__(self):
        return "Range({0}, {1})".format(self.minimum, self.maximum)

    def __contains__(self, value):
        return self.minimum <= value <= self.maximum

    @staticmethod
    def inclusive(minimum, maximum):
        return Range(minimum, maximum)

    @staticmethod
    def exactly(value):
        return Range(value, value)

    @staticmethod
    def at_least(minimum_value):
        return Range(minimum_value, float("inf"))


class Gaussian(object):

    def __init__(self, mean=0.0, stdev=1.0):
        self.mean = mean
        self.stdev = stdev
        self.variance = stdev ** 2.0

        if self.variance != 0.0:
            self.precision = 1.0 / self.variance
            self.precision_mean = self.precision * self.mean
        else:
            self.precision = float("inf")
            if self.mean == 0.0:
                self.precision_mean = 0.0
            else:
                self.precision_mean = float("inf")

    def __str__(self):
        return "mean=%.4f stdev=%.4f" % (self.mean, self.stdev)

    def __copy__(self):
        result = Gaussian()
        result.mean = self.mean
        result.stdev = self.stdev
        result.variance = self.variance
        result.precision = self.precision
        result.precision_mean = self.precision_mean
        return result

    def normalization_constant(self):
        return 1.0 / SQRT_2_PI * self.stdev

    @staticmethod
    def from_precision_mean(precision_mean, precision):
        result = Gaussian()
        result.precision = precision
        result.precision_mean = precision_mean

        if precision != 0.0:
            result.variance = 1.0 / precision
            result.stdev = sqrt(result.variance)
            result.mean = result.precision_mean / result.precision
        else:
            result.variance = float("inf")
            result.stdev = float("inf")
            result.mean = float("inf")

        return result

    def __mul__(self, other):
        return Gaussian.from_precision_mean(
            self.precision_mean + other.precision_mean,
            self.precision + other.precision)

    def __sub__(self, other):
        # this is the absolute difference
        return max(
            abs(self.precision_mean - other.precision_mean),
            sqrt(abs(self.precision - other.precision)))

    @staticmethod
    def log_product_normalization(left, right):
        if left.precision == 0.0 or right.precision == 0.0:
            return 0.0

        variance_sum = left.variance + right.variance
        mean_difference = left.mean - right.mean

        return -LOG_SQRT_2_PI - (log(variance_sum) / 2.0) - ((mean_difference ** 2.0) / (2.0 * variance_sum))

    def __truediv__(self, other):
        return Gaussian.from_precision_mean(
            self.precision_mean - other.precision_mean,
            self.precision - other.precision)

    @staticmethod
    def log_ratio_normalization(numerator, denominator):
        if numerator.precision == 0.0 or denominator.precision == 0.0:
            return 0.0

        variance_difference = denominator.variance - numerator.variance
        mean_difference = numerator.mean - denominator.mean

        return (log(denominator.variance) +
                LOG_SQRT_2_PI -
                log(variance_difference) / 2.0 +
                (mean_difference ** 2.0) / (2.0 * variance_difference))

    @staticmethod
    def at(x, mean=0.0, stdev=1.0):
        multiplier = 1.0 / (stdev * SQRT_2_PI)
        exp_part = exp((-1.0 * (x - mean) ** 2.0) / (2.0 * (stdev ** 2.0)))
        result = multiplier * exp_part
        return result

    @staticmethod
    def cumulative_to(x, mean=0.0, stdev=1.0):
        result = Gaussian.error_function_cumulative_to(INV_SQRT_2 * x)
        return 0.5 * result

    @staticmethod
    def error_function_cumulative_to(x):
        z = abs(x)

        t = 2.0 / (2.0 + z)
        ty = 4.0 * t - 2.0

        coefficients = [-1.3026537197817094,
                        6.4196979235649026e-1,
                        1.9476473204185836e-2,
                        - 9.561514786808631e-3,
                        - 9.46595344482036e-4,
                        3.66839497852761e-4,
                        4.2523324806907e-5,
                        - 2.0278578112534e-5,
                        - 1.624290004647e-6,
                        1.303655835580e-6,
                        1.5626441722e-8,
                        - 8.5238095915e-8,
                        6.529054439e-9,
                        5.059343495e-9,
                        - 9.91364156e-10,
                        - 2.27365122e-10,
                        9.6467911e-11,
                        2.394038e-12,
                        - 6.886027e-12,
                        8.94487e-13,
                        3.13092e-13,
                        - 1.12708e-13,
                        3.81e-16,
                        7.106e-15,
                        - 1.523e-15,
                        - 9.4e-17,
                        1.21e-16,
                        - 2.8e-17]

        d = 0.0
        dd = 0.0

        for coef in reversed(coefficients[1:]):
            tmp = d
            d = ty * d - dd + coef
            dd = tmp

        ans = t * exp(-z * z + 0.5 * (coefficients[0] + ty * d) - dd)
        return ans if x >= 0.0 else 2.0 - ans

    @staticmethod
    def inverse_error_function_cumulative_to(p):
        if p >= 2.0:
            return -100.0
        if p <= 0.0:
            return 100.0

        pp = p if p < 1.0 else 2.0 - p
        t = sqrt(-2.0 * log(pp / 2.0))
        x = -0.70711 * ((2.30753 + t * 0.27061) / (1.0 + t * (0.99229 + t * 0.04481)) - t)

        for _ in range(2):
            err = Gaussian.error_function_cumulative_to(x) - pp
            x += err / (1.12837916709551257 * exp(-(x ** 2.0)) - x * err)

        return x if p < 1.0 else -x

    @staticmethod
    def inverse_cumulative_to(x, mean=0.0, stdev=1.0):
        return mean - sqrt(2.0) * stdev * Gaussian.inverse_error_function_cumulative_to(2.0 * x)
