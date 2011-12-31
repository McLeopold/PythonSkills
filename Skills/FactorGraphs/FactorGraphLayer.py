from Schedule import ScheduleSequence

class FactorGraphLayer():

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
        raise NotImplementedError("build_layer not implemented")

    def create_prior_schedule(self):
        return None

    def create_posterior_schedule(self):
        return None
