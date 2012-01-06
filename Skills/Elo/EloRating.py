from Skills.Rating import Rating, RatingError
from collections import Sequence

class EloRating(Rating):

    DEFAULT_K_FACTOR = 32.0 # ICC Default

    def __init__(self, mean, k_factor=DEFAULT_K_FACTOR):
        Rating.__init__(self, mean)
        try:
            self.k_factor = float(k_factor)
        except:
            RatingError("EloRating k_factor value must be numeric")

    def __repr__(self):
        return "EloRating(%s, %s)" % (self.mean, self.k_factor)

    def __str__(self):
        return "mean=%.4f, k_factor=%d" % (self.mean, self.k_factor)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'k_factor')):
            if isinstance(rating, Sequence):
                try:
                    return EloRating(*rating)
                except TypeError:
                    raise RatingError("EloRating must be a sequence of length 1 or 2 or a EloRating object")
            else:
                try:
                    return EloRating(rating)
                except TypeError:
                    raise RatingError("EloRating was passed the wrong number of arguments")
        else:
            return rating
