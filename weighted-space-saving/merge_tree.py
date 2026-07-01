from weighted_space_saving import WeightedSpaceSaving
from helpers import merge

class MergeTree: 
    def __init__(self, capacity: int, dur: int): 
        self.cap = capacity
        self.dur = dur # duration of each epoch
        self.q = [] # (WeightedSpaceSaving, start_time) pairs
        self.done = [] 
        self.cur = WeightedSpaceSaving(capacity=capacity)   
        self.cur_epoch = 0

    def offer(self, t, el, val):
        # route event to current epoch's sketch
        # first event from a new epoch triggers the closing of the previous one
        epoch = t // self.dur 
        if epoch != self.cur_epoch:
            self._close(self.cur_epoch * self.dur)
            self.cur_epoch = epoch
        self.cur.offer(el, val)

    def _close(self, t):
        # t = start time of cur interval
        end_time = t + self.dur
        self.done.append((self.cur, t, end_time))
        carry, carry_start_time = self.cur, t
        self.cur = WeightedSpaceSaving(capacity=self.cap) # reset
        lvl = 0

        while lvl < len(self.q) and self.q[lvl]: 
            # absorb pending sketch, grow interval backwards (from start side), clear slot, carry upwards
            prev_sketch, prev_start_time = self.q[lvl]
            carry = merge(prev_sketch, carry, self.cap)
            carry_start_time = prev_start_time
            self.q[lvl] = None
            lvl += 1

        if lvl == len(self.q):
            self.q.append(None)
        self.q[lvl] = (carry, carry_start_time)

    def query(self, t1, t2, k):
        # find completed sketches with start >= t1 and end <= t2
        # pairwise-merge the sketches 
        # return topk(k) of the merged sketch

        sets = [s for (s, start, end) in self.done if start >= t1 and end <= t2]

        if not sets: 
            return [] 
        
        merged = sets[0]
        for s in sets[1:]:
            merged = merge(merged, s, self.cap)

        return merged.topk(k)
