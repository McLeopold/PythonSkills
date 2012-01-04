from GaussianFactor import GaussianFactor, Gaussian, Message
from math import sqrt
from copy import copy

class GaussianPriorFactor(GaussianFactor):
    '''
    Supplies the factor graph with prior information
    '''


    def __init__(self, mean, variance, variable):
        GaussianFactor.__init__(self, "Prior value going to %s" % variable)
        self.new_message = Gaussian(mean, sqrt(variance))
        new_message = Message(Gaussian.from_precision_mean(0, 0),
                              "message from %s to %s" % (self, variable))
        self.create_variable_to_message_binding_with_message(variable, new_message)

    def update_message_variable(self, message, variable):
        old_marginal = copy(variable.value)
        old_message = message
        new_marginal = Gaussian.from_precision_mean(
            old_marginal.precision_mean + self.new_message.precision_mean - old_message.value.precision_mean,
            old_marginal.precision + self.new_message.precision - old_message.value.precision)

        variable.value = new_marginal
        new_message = self.new_message
        message.value = new_message
        return old_marginal - new_marginal
