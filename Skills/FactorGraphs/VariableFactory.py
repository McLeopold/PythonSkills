from Variable import Variable, KeyedVariable

class VariableFactory(object):

    def __init__(self, variable_prior_initializer):
        self.variable_prior_initializer = variable_prior_initializer

    def create_basic_variable(self, name):
        return Variable(name, self.variable_prior_initializer())

    def create_keyed_variable(self, key, name):
        return KeyedVariable(key, name, self.variable_prior_initializer())
