from Skills.FactorGraphs.Factor import Factor
from Skills.FactorGraphs.Message import Message
from Skills.Numerics.Gaussian import Gaussian

class GaussianFactor(Factor):

    def send_message_variable(self, message, variable):
        marginal = variable.value
        message_value = message.value
        log_z = Gaussian.log_product_normalization(marginal, message_value)
        variable.value = marginal * message_value
        return log_z

    def create_variable_to_message_binding(self, variable):
        new_distribution = Gaussian.from_precision_mean(0.0, 0.0)
        binding = Factor.create_variable_to_message_binding_with_message(
            self,
            variable,
            Message(new_distribution,
                    "message from %s to %s" % (self, variable))
                                                                         )
        return binding
