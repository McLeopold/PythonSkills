class RangeError(Exception):
    pass

class Range():
    def __init__(self, minimum, maximum):
        if minimum > maximum:
            raise RangeError("minimum > maximum")

        self.minimum = minimum
        self.maximum = maximum

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
        return  Range(minimum_value, float("inf"))