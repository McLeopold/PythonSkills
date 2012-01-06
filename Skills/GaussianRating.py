from Skills.Numerics.Gaussian import Gaussian
from Skills.Rating import Rating, RatingError
from collections import Sequence

class GaussianRating(Rating):
    '''
    Constructs a rating.
    '''

    rating_class = None

    def __init__(self, mean, stdev):
        Rating.__init__(self, mean)
        try:
            self.stdev = float(stdev)
        except ValueError:
            raise RatingError("GaussianRating stdev value must be numeric")

    def __repr__(self):
        return "GaussianRating(%s, %s)" % (self.mean, self.stdev)

    def __str__(self):
        return "mean=%.5f, stdev=%.5f" % (self.mean, self.stdev)

    def conservative_rating(self, game_info):
        return self.mean - game_info.conservative_stdev_multiplier * self.stdev

    def partial_update(self, prior, full_posterior, update_percentage):
        prior_gaussian = Gaussian(prior.mean, prior.stdev)
        posterior_gaussian = Gaussian(full_posterior.mean, full_posterior.stdev)

        precision_difference = posterior_gaussian.precision - prior_gaussian.precision
        partial_precision_difference = update_percentage * precision_difference

        precision_mean_difference = posterior_gaussian.precision_mean - prior_gaussian.precision_mean
        partial_precision_mean_difference = update_percentage * precision_mean_difference

        partial_posterior_gaussian = Gaussian.from_precision_mean(
            prior_gaussian.precision_mean + partial_precision_mean_difference,
            prior_gaussian.precision + partial_precision_difference)

        return Rating(partial_posterior_gaussian.mean, partial_posterior_gaussian.stdev)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'stdev')):
            if isinstance(rating, Sequence):
                try:
                    return GaussianRating(*rating)
                except TypeError:
                    raise RatingError("GaussianRating must be a sequence of length 2 or a GaussianRating object")
            else:
                try:
                    return GaussianRating(rating)
                except TypeError:
                    raise RatingError("GaussianRating was passed the wrong number of arguments")
        else:
            return rating
