from GaussianFactor import GaussianFactor, Gaussian
from copy import copy

class GaussianLikelihoodFactorError(Exception):
    pass

class GaussianLikelihoodFactor(GaussianFactor):
    '''
    Connects two variables and adds uncertainty
    
    See the accompanying math paper for more details
    '''


    def __init__(self, beta_squared, variable1, variable2):
        GaussianFactor.__init__(self, "Likelihood of %s going to %s" % (variable2, variable1))
        self.precision = 1.0 / beta_squared
        self.create_variable_to_message_binding(variable1)
        self.create_variable_to_message_binding(variable2)

    def log_normalization(self):
        return Gaussian.log_ratio_normalization(
            self.variables[0].value,
            self.messages[0].value
        )

    def update_helper(self, message1, message2, variable1, variable2):
        message1_value = copy(message1.value)
        message2_value = copy(message2.value)

        marginal1 = copy(variable1.value)
        marginal2 = copy(variable2.value)

        a = self.precision / (self.precision + marginal2.precision - message2_value.precision)

        new_message = Gaussian.from_precision_mean(
            a * (marginal2.precision_mean - message2_value.precision_mean),
            a * (marginal2.precision - message2_value.precision))

        old_marginal_without_message = marginal1 / message1_value

        new_marginal = old_marginal_without_message * new_message

        message1.value = new_message
        variable1.value = new_marginal

        return new_marginal - marginal1

    def update_message_index(self, message_index):
        if message_index not in (0, 1):
            raise GaussianLikelihoodFactorError("GaussianLikelihoodFactorError message index not in [0, 1]")

        i, j = message_index, 1 - message_index
        return self.update_helper(self.messages[i], self.messages[j],
                                  self.variables[i], self.variables[j])
