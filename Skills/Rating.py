from Numerics.GaussianDistribution import GaussianDistribution

class RatingError(Exception):
    pass

class Rating():
    '''
    Constructs a rating.
    '''

    def __init__(self, mean,
                       stdev):
        try:
            self.mean = float(mean)
            self.stdev = float(stdev)
        except ValueError:
            raise RatingError("Rating values must be numeric")

    def __repr__(self):
        return "Rating(%s, %s)" % (self.mean, self.stdev)

    def __str__(self):
        return "mean=%.5f, stdev=%.5f" % (self.mean, self.stdev)

    def conservative_rating(self, game_info):
        return self.mean - game_info.conservative_stdev_multiplier * self.stdev

    def partial_update(self, prior, full_posterior, update_percentage):
        prior_gaussian = GaussianDistribution(prior.mean, prior.stdev)
        posterior_gaussian = GaussianDistribution(full_posterior.mean, full_posterior.stdev)

        precision_difference = posterior_gaussian.precision - prior_gaussian.precision
        partial_precision_difference = update_percentage * precision_difference

        precision_mean_difference = posterior_gaussian.precision_mean - prior_gaussian.precision_mean
        partial_precision_mean_difference = update_percentage * precision_mean_difference

        partial_posterior_gaussian = GaussianDistribution.from_precision_mean(
            prior_gaussian.precision_mean + partial_precision_mean_difference,
            prior_gaussian.precision + partial_precision_difference)

        return Rating(partial_posterior_gaussian.mean, partial_posterior_gaussian.stdev)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'stdev')):
            try:
                return Rating(*rating)
            except TypeError:
                raise RatingError("rating must be a sequence of length 2 or 3 or a Rating object")
        else:
            return rating
