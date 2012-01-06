class Schedule(object):
    log = None # can be set globally for all instances

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
        if self.log:
            self.log("d %02d : %.4f step     %s (%s=%s)" % (depth, delta, self.name, self.index, self.factor))
        return delta

class ScheduleSequence(Schedule):
    def __init__(self, name, schedules):
        Schedule.__init__(self, name)
        self.schedules = schedules

    def visit(self, depth= -1, max_depth=0):
        if self.log:
            self.log("d %02d :        sequence visit %s" % (depth, self.name))
        max_delta = 0
        for schedule in self.schedules:
            current_visit = schedule.visit(depth + 1, max_depth)
            max_delta = max(current_visit, max_delta)
        if self.log:
            self.log("d %02d : %.4f sequence %s" % (depth, max_delta, self.name))
        return max_delta

class ScheduleLoop(Schedule):
    def __init__(self, name, schedule_to_loop, max_delta):
        Schedule.__init__(self, name)
        self.schedule_to_loop = schedule_to_loop
        self.max_delta = max_delta

    def visit(self, depth= -1, max_depth=0):
        if self.log:
            self.log("d %02d :        loop     visit %s" % (depth, self.name))
        total_iterations = 1
        delta = self.schedule_to_loop.visit(depth + 1, max_depth)
        while delta > self.max_delta:
            delta = self.schedule_to_loop.visit(depth + 1, max_depth)
            if self.log:
                self.log("d %02d : %.4f loop %03d %s" % (depth, delta, total_iterations, self.name))
            total_iterations += 1

        return delta
