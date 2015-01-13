from __future__ import division
from math import sqrt, log
from copy import copy

from skills.factorgraph import (
    Factor,
    Message,
    )

from skills.numerics import Gaussian

from skills.trueskill.truncated import (
    v_exceeds_margin,
    v_within_margin,
    w_exceeds_margin,
    w_within_margin,
    )


class GaussianLikelihoodFactorError(Exception):
    pass


class GaussianWeightedSumFactorError(Exception):
    pass


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


class GaussianGreaterThanFactor(GaussianFactor):

    def __init__(self, epsilon, variable):
        GaussianFactor.__init__(self, "%s > %.2f" % (variable, epsilon))
        self.epsilon = epsilon
        self.create_variable_to_message_binding(variable)

    def log_normalization(self):
        marginal = self.variables[0].value
        message = self.messages[0].value
        message_from_variable = marginal / message

        return (-Gaussian.log_product_normalization(message_from_variable, message) +
                log(Gaussian.cumulative_to((message_from_variable.mean - self.epsilon)
                                                       / message_from_variable.stdev)))

    def update_message_variable(self, message, variable):
        old_marginal = copy(variable.value)
        old_message = copy(message.value)
        message_from_var = old_marginal / old_message

        c = message_from_var.precision
        d = message_from_var.precision_mean

        sqrt_c = sqrt(c)
        d_on_sqrt_c = d / sqrt_c

        epsilon_times_sqrt_c = self.epsilon * sqrt_c
        d = message_from_var.precision_mean

        denom = 1.0 - w_exceeds_margin(d_on_sqrt_c, epsilon_times_sqrt_c)

        new_precision = c / denom
        new_precision_mean = (d + sqrt_c * v_exceeds_margin(d_on_sqrt_c, epsilon_times_sqrt_c)) / denom

        new_marginal = Gaussian.from_precision_mean(new_precision_mean, new_precision)
        new_message = (old_message * new_marginal) / old_marginal

        message.value = new_message
        variable.value = new_marginal

        return new_marginal - old_marginal


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


class GaussianWeightedSumFactor(GaussianFactor):
    '''
    Factor that sums together multiple Gaussians
    '''

    def __init__(self, sum_variable, variables_to_sum, variable_weights=None):
        GaussianFactor.__init__(self, self.create_name(sum_variable, variables_to_sum, variable_weights))
        self.weights = []
        self.weights_squared = []

        # the first weights are a straightforward copy
        self.weights.append(variable_weights[:])
        self.weights_squared.append(list(map(lambda x: x ** 2, variable_weights)))

        # 0..n-1
        self.variable_index_orders_for_weights = [list(range(len(variables_to_sum) + 1))]

        for weights_index in range(1, len(variable_weights) + 1):
            current_weights = [0.0 for _ in range(len(variable_weights))]
            variable_indexes = [0.0 for _ in range(len(variable_weights) + 1)]
            variable_indexes[0] = weights_index

            current_weights_squared = [0 for _ in range(len(variable_weights))]

            current_destination_weight_index = 0
            for current_weight_source_index in range(len(variable_weights)):
                if current_weight_source_index == weights_index - 1:
                    continue

                try:
                    current_weight = -variable_weights[current_weight_source_index] / variable_weights[weights_index - 1]
                except ZeroDivisionError:
                    current_weight = 0.0

                current_weights[current_destination_weight_index] = current_weight
                current_weights_squared[current_destination_weight_index] = current_weight ** 2.0

                variable_indexes[current_destination_weight_index + 1] = current_weight_source_index + 1
                current_destination_weight_index += 1

            try:
                final_weight = 1.0 / variable_weights[weights_index - 1]
            except ZeroDivisionError:
                final_weight = 0.0

            current_weights[current_destination_weight_index] = final_weight
            current_weights_squared[current_destination_weight_index] = final_weight ** 2.0
            variable_indexes[-1] = 0
            self.variable_index_orders_for_weights.append(variable_indexes)

            self.weights.append(current_weights)
            self.weights_squared.append(current_weights_squared)

        self.create_variable_to_message_binding(sum_variable)
        for current_variable in variables_to_sum:
            local_current_variable = current_variable
            self.create_variable_to_message_binding(local_current_variable)


    def log_normalization(self):
        result = 0.0
        for i in range(1, len(self.variables)):
            result += Gaussian.log_ratio_normalization(self.variables[i].value, self.messages[i].value)

        return result

    def update_helper(self, weights, weights_squared, messages, variables):
        message0 = copy(messages[0].value)
        marginal0 = copy(variables[0].value)

        inverse_of_new_precision_sum = 0.0
        another_inverse_of_new_precision_sum = 0.0
        weighted_mean_sum = 0.0
        another_weighted_mean_sum = 0.0

        for i in range(len(weights_squared)):
            inverse_of_new_precision_sum += weights_squared[i] / (variables[i + 1].value.precision - messages[i + 1].value.precision)

            diff = variables[i + 1].value / messages[i + 1].value
            another_inverse_of_new_precision_sum += weights_squared[i] / diff.precision

            weighted_mean_sum += (weights[i] *
                                  (variables[i + 1].value.precision_mean - messages[i + 1].value.precision_mean) /
                                  (variables[i + 1].value.precision - messages[i + 1].value.precision))
            another_weighted_mean_sum += weights[i] * diff.precision_mean / diff.precision

        new_precision = 1.0 / inverse_of_new_precision_sum
        #another_new_precision = 1.0 / another_inverse_of_new_precision_sum

        new_precision_mean = new_precision * weighted_mean_sum
        #another_new_precision_mean = another_new_precision * another_weighted_mean_sum

        new_message = Gaussian.from_precision_mean(new_precision_mean, new_precision)
        old_marginal_without_message = marginal0 / message0

        new_marginal = old_marginal_without_message * new_message

        messages[0].value = new_message
        variables[0].value = new_marginal

        final_diff = new_marginal - marginal0
        return final_diff

    def update_message_index(self, message_index):
        try:
            updated_messages = []
            updated_variables = []

            indexes_to_use = self.variable_index_orders_for_weights[message_index]
            for i in range(len(self.messages)):
                updated_messages.append(self.messages[indexes_to_use[i]])
                updated_variables.append(self.variables[indexes_to_use[i]])

            return self.update_helper(self.weights[message_index],
                                      self.weights_squared[message_index],
                                      updated_messages,
                                      updated_variables)
        except IndexError:
            raise GaussianWeightedSumFactorError("message index is not in valid range")

    def create_name(self, sum_variable, variables_to_sum, weights):
        result = str(sum_variable)
        result += " = "

        for i in range(len(variables_to_sum)):
            if i == 0 and weights[i] < 0:
                result += '-'

            abs_value = "%.2f" % abs(weights[i])
            result += abs_value
            result += '*['
            result += str(variables_to_sum[i])
            result += ']'

            if i < len(variables_to_sum) - 1:
                if weights[i + 1] >= 0:
                    result += ' + '
                else:
                    result += ' - '

        return result

    def create_variable_to_message_binding(self, variable):
        GaussianFactor.create_variable_to_message_binding(self, variable)

    def create_variable_to_message_binding_with_message(self, variable, message):
        GaussianFactor.create_variable_to_message_binding_with_message(self, variable, message)


class GaussianWithinFactor(GaussianFactor):
    '''
    Factor representing a team difference that has not exceeded the draw margin
    '''

    def __init__(self, epsilon, variable):
        GaussianFactor.__init__(self, "%s <= %.2f" % (variable, epsilon))
        self.epsilon = epsilon
        self.create_variable_to_message_binding(variable)

    def log_normalization(self):
        marginal = self.variables[0].value
        message = self.messages[0].value
        message_from_variable = marginal / message
        mean = message_from_variable.mean
        std = message_from_variable.stdev
        z = (Gaussian.cumulative_to((self.epsilon - mean) / std) -
             Gaussian.cumulative_to((-self.epsilon - mean) / std))

        return -Gaussian.log_product_normalization(message_from_variable, message) + log(z)

    def update_message_variable(self, message, variable):
        old_marginal = copy(variable.value)
        old_message = copy(message.value)
        message_from_variable = old_marginal / old_message

        c = message_from_variable.precision
        d = message_from_variable.precision_mean

        sqrt_c = sqrt(c)
        d_on_sqrt_c = d / sqrt_c

        epsilon_times_sqrt_c = self.epsilon * sqrt_c
        d = message_from_variable.precision_mean

        denominator = 1.0 - w_within_margin(d_on_sqrt_c, epsilon_times_sqrt_c)
        new_precision = c / denominator
        new_precision_mean = (d + sqrt_c * v_within_margin(d_on_sqrt_c, epsilon_times_sqrt_c)) / denominator

        new_marginal = Gaussian.from_precision_mean(new_precision_mean, new_precision)
        new_message = (old_message * new_marginal) / old_marginal

        message.value = new_message
        variable.value = new_marginal

        return new_marginal - old_marginal
