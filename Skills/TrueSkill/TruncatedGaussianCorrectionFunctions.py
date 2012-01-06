from Skills.Numerics.Gaussian import Gaussian

class TruncatedGaussianCorrectionFunctions(object):
    '''
    These functions from the bottom of page 4 of the TrueSkill paper
    '''

    @staticmethod
    def v_exceeds_margin_scaled(team_performance_difference, draw_margin, c):
        return TruncatedGaussianCorrectionFunctions.v_exceeds_margin(team_performance_difference / c, draw_margin / c)

    @staticmethod
    def v_exceeds_margin(team_performance_difference, draw_margin):
        denominator = Gaussian.cumulative_to(team_performance_difference - draw_margin)
        if (denominator < 2.22275874e-162):
            return -team_performance_difference + draw_margin
        return Gaussian.at(team_performance_difference - draw_margin) / denominator

    @staticmethod
    def w_exceeds_margin_scaled(team_performance_difference, draw_margin, c):
        return TruncatedGaussianCorrectionFunctions.w_exceeds_margin(team_performance_difference / c, draw_margin / c)

    @staticmethod
    def w_exceeds_margin(team_performance_difference, draw_margin):
        denominator = Gaussian.cumulative_to(team_performance_difference - draw_margin)
        if denominator < 2.222758749e-162:
            if team_performance_difference < 0.0:
                return 1.0
            return 0.0
        v_win = TruncatedGaussianCorrectionFunctions.v_exceeds_margin(team_performance_difference, draw_margin)
        return v_win * (v_win + team_performance_difference - draw_margin)

    @staticmethod
    def v_within_margin_scaled(team_performance_difference, draw_margin, c):
        return TruncatedGaussianCorrectionFunctions.v_within_margin(team_performance_difference / c, draw_margin / c)

    @staticmethod
    def v_within_margin(team_performance_difference, draw_margin):
        team_performance_difference_abs = abs(team_performance_difference)
        denominator = (
            Gaussian.cumulative_to(draw_margin - team_performance_difference_abs) -
            Gaussian.cumulative_to(-draw_margin - team_performance_difference_abs))

        if denominator < 2.222758749e-162:
            if team_performance_difference < 0.0:
                return -team_performance_difference - draw_margin
            return -team_performance_difference + draw_margin

        numerator = (Gaussian.at(-draw_margin - team_performance_difference_abs) -
                     Gaussian.at(draw_margin - team_performance_difference_abs))

        if team_performance_difference < 0.0:
            return -numerator / denominator
        return numerator / denominator

    @staticmethod
    def w_within_margin_scaled(team_performance_difference, draw_margin, c):
        return TruncatedGaussianCorrectionFunctions.w_within_margin(team_performance_difference / c, draw_margin / c)

    @staticmethod
    def w_within_margin(team_performance_difference, draw_margin):
        team_performance_difference_abs = abs(team_performance_difference)
        denominator = (Gaussian.cumulative_to(draw_margin - team_performance_difference_abs) -
                       Gaussian.cumulative_to(-draw_margin - team_performance_difference_abs))

        if denominator < 2.222758749e-162:
            return 1.0

        vt = TruncatedGaussianCorrectionFunctions.v_within_margin(team_performance_difference_abs, draw_margin)

        return (vt ** 2 +
                (
                    (draw_margin - team_performance_difference_abs) *
                    Gaussian.at(draw_margin - team_performance_difference_abs) -
                    (-draw_margin - team_performance_difference_abs) *
                    Gaussian.at(-draw_margin - team_performance_difference_abs)) / denominator)

