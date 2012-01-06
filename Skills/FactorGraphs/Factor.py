class FactorError(Exception):
    pass

class Factor(object):
    def __init__(self, name):
        self.messages = []
        self.variables = []

        self.name = name
        self.message_to_variable_binding = {}

    def __str__(self):
        return self.name if self.name is not None else self.__class__.__name__

    def log_normalization(self):
        return 0

    def update_message_index(self, message_index):
        try:
            message = self.messages[message_index]
            variable = self.message_to_variable_binding[message]
            return self.update_message_variable(message, variable)
        except IndexError:
            raise FactorError("message_index is an invalid index")

    def update_message_variable(self, message, variable):
        raise NotImplementedError

    def reset_marginals(self):
        for current_variable in self.message_to_variable_binding.values():
            current_variable.reset_to_prior

    def send_message_index(self, message_index):
        try:
            message = self.messages[message_index]
            variable = self.message_to_variable_binding[message]
            return self.send_message_variable(message, variable)
        except IndexError:
            raise FactorError("message_index is an invalid index")

    def create_variable_to_message_binding_with_message(self, variable, message):
        self.messages.append(message)
        self.variables.append(variable)
        self.message_to_variable_binding[message] = variable
        return message
