from Skills.Numerics.GaussianDistribution import GaussianDistribution
from math import sqrt

class DrawMargin(object):

    @staticmethod
    def draw_margin_from_draw_probability(draw_probability, beta):
        return (GaussianDistribution.inverse_cumulative_to(0.5 * (draw_probability + 1), 0, 1) *
                sqrt(1 + 1) * beta)
