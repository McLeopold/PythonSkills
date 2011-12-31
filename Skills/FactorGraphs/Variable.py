class VariableError(Exception):
    pass

class Variable():

    def __init__(self, name, prior):
        self.name = "Variable[%s]" % name
        self.prior = prior
        self.reset_to_prior()

    def __str__(self):
        return self.name

    def reset_to_prior(self):
        self.value = self.prior

class DefaultVariable(Variable):
    def __init__(self):
        Variable.__init__(self, "Default", None)

    def __setattr__(self, name, value):
        if name == 'value':
            raise VariableError("DefaultVariable attribute value can not be changed")
        else:
            super(DefaultVariable, self).__setattr(name, value)

class KeyedVariable(Variable):
    def __init__(self, key, name, prior):
        Variable.__init__(self, name, prior)
        self.key = key
