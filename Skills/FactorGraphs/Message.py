class Message(object):

    def __init__(self, value=None, name=None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name
