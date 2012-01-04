class RatingError(Exception):
    pass

class Rating():
    '''
    Constructs a rating.
    '''

    def __init__(self, mean):
        try:
            self.mean = float(mean)
        except ValueError:
            raise RatingError("Rating mean value must be numeric")

    def __repr__(self):
        return "Rating(%s)" % (self.mean)

    def __str__(self):
        return "mean=%.5f" % (self.mean)

    def __pow__(self, other):
        return self.mean ** other

    def __rpow__(self, other):
        return other ** self.mean

    def __div__(self, other):
        return self.mean / other

    def __add__(self, other):
        try:
            return Rating(self.mean + other.mean)
        except AttributeError:
            return self.mean + other

    def __sub__(self, other):
        try:
            return Rating(self.mean - other.mean)
        except AttributeError:
            return self.mean - other

    @staticmethod
    def ensure_rating(rating):
        if (not hasattr(rating, 'mean')):
            try:
                return Rating(rating)
            except TypeError:
                raise RatingError("Rating was not given the correct amount of arguments")
        else:
            return rating

class RatingFactory(object):
    rating_class = Rating

    def __new__(self):
        return RatingFactory.rating_class()

    @staticmethod
    def ensure_rating(rating):
        return RatingFactory.rating_class.ensure_rating(rating)
