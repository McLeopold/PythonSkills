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
