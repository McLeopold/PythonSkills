from GaussianFactor import GaussianFactor, GaussianDistribution
from copy import copy

class GaussianWeightedSumFactorError(Exception):
    pass

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
        self.weights_squared.append(map(lambda x: x ** 2, variable_weights))

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
            result += GaussianDistribution.log_ratio_normalization(self.variables[i].value, self.messages[i].value)

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
        another_new_precision = 1.0 / another_inverse_of_new_precision_sum

        new_precision_mean = new_precision * weighted_mean_sum
        another_new_precision_mean = another_new_precision * another_weighted_mean_sum

        new_message = GaussianDistribution.from_precision_mean(new_precision_mean, new_precision)
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
