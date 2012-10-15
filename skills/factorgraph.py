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
            raise IndexError("message_index is an invalid index")

    def update_message_variable(self, message, variable):
        raise NotImplementedError

    def reset_marginals(self):
        for current_variable in self.message_to_variable_binding.values():
            current_variable.reset_to_prior

    def send_message_variable(self, message, variable):
        raise NotImplementedError

    def send_message_index(self, message_index):
        try:
            message = self.messages[message_index]
            variable = self.message_to_variable_binding[message]
            return self.send_message_variable(message, variable)
        except IndexError:
            raise IndexError("message_index is an invalid index")

    def create_variable_to_message_binding_with_message(self, variable, message):
        self.messages.append(message)
        self.variables.append(variable)
        self.message_to_variable_binding[message] = variable
        return message


class FactorGraph(object):

    def __init__(self):
        self.variable_factory = None


class FactorGraphLayer(object):

    def __init__(self, parent_graph):
        self._local_factors = []
        self.output_variables_groups = []
        self.input_variables_groups = []
        self.parent_factor_graph = parent_graph

    def local_factors(self):
        return self._local_factors

    def schedule_sequence(self, items_to_sequence, name):
        return ScheduleSequence(name, items_to_sequence)

    def add_layer_factor(self, factor):
        self._local_factors.append(factor)

    def build_layer(self):
        raise NotImplementedError

    def create_prior_schedule(self):
        return None

    def create_posterior_schedule(self):
        return None


class FactorList(list):
    '''
    Helper class for computing the factor graph's normalization constant
    '''

    def log_normalization(self):
        for current_factor in self:
            current_factor.reset_marginals()

        sum_log_z = 0.0
        for f in self:
            for j in range(len(f.messages)):
                sum_log_z += f.send_message_index(j)

        sum_log_s = 0
        for current_factor in self:
            sum_log_s += current_factor.log_normalization()

        return sum_log_z + sum_log_s


class Message(object):

    def __init__(self, value=None, name=None):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name


class Schedule(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def visit(self, depth= -1, max_depth=0):
        raise NotImplementedError


class ScheduleStep(Schedule):

    def __init__(self, name, factor, index):
        Schedule.__init__(self, name)
        self.factor = factor
        self.index = index

    def visit(self, depth= -1, max_depth=0):
        delta = self.factor.update_message_index(self.index)
        return delta


class ScheduleSequence(Schedule):

    def __init__(self, name, schedules):
        Schedule.__init__(self, name)
        self.schedules = schedules

    def visit(self, depth= -1, max_depth=0):
        max_delta = 0
        for schedule in self.schedules:
            current_visit = schedule.visit(depth + 1, max_depth)
            max_delta = max(current_visit, max_delta)
        return max_delta


class ScheduleLoop(Schedule):

    def __init__(self, name, schedule_to_loop, max_delta):
        Schedule.__init__(self, name)
        self.schedule_to_loop = schedule_to_loop
        self.max_delta = max_delta

    def visit(self, depth= -1, max_depth=0):
        total_iterations = 1
        delta = self.schedule_to_loop.visit(depth + 1, max_depth)
        while delta > self.max_delta:
            delta = self.schedule_to_loop.visit(depth + 1, max_depth)
            total_iterations += 1
        return delta


class Variable(object):

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
            raise AttributeError("DefaultVariable attribute value can not be changed")
        else:
            super(DefaultVariable, self).__setattr(name, value)


class KeyedVariable(Variable):

    def __init__(self, key, name, prior):
        Variable.__init__(self, name, prior)
        self.key = key


class VariableFactory(object):

    def __init__(self, variable_prior_initializer):
        self.variable_prior_initializer = variable_prior_initializer

    def create_basic_variable(self, name):
        return Variable(name, self.variable_prior_initializer())

    def create_keyed_variable(self, key, name):
        return KeyedVariable(key, name, self.variable_prior_initializer())
