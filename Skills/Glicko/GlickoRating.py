from Skills.Rating import RatingError
from Skills.GaussianRating import GaussianRating
from collections import Sequence

class GlickoRating(GaussianRating):

    def __init__(self, mean, stdev, last_rating_period=None):
        GaussianRating.__init__(self, mean, stdev)
        self.last_rating_period = last_rating_period

    def __repr__(self):
        return "GlickoRating(%s, %s, %s)" % (self.mean, self.stdev, self.last_rating_period)

    def __str__(self):
        return "mean=%.4f, stdev=%.4f, last_rating_period=%d" % (self.mean, self.stdev, self.last_rating_period)

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean') or
                not hasattr(rating, 'stdev') or
                not hasattr(rating, 'last_rating_period')):
            if isinstance(rating, Sequence):
                try:
                    return GlickoRating(*rating)
                except TypeError:
                    raise RatingError("GlickoRating must be a sequence of length 2 or 3 or a GlickoRating object")
            else:
                try:
                    return GlickoRating(rating)
                except TypeError:
                    raise RatingError("GlickoRating was passed the wrong number of arguments")
        else:
            return rating
