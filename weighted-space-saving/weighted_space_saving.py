class WeightedSpaceSaving:
    """
    Improvement of the Space-Saving algorithm for weighted data streams.
    """

    def __init__(self, capacity: int): 
        self.cap = capacity 
        self.estimates = {} # el -> estimate weight
        self.errors = {} # el -> error bound

    @property
    def min_estimate(self): 
        return min(self.estimates.values(), default=0)

    def offer(self, el, val):
        # add to stream
        if el in self.estimates: 
            self.estimates[el] += val
            return 

        # element not in map
        if len(self.estimates) < self.cap:
            self.estimates[el] = val
            self.errors[el] = 0
            return 

        # evict the min-estimate element
        lowest = min(self.estimates, key=self.estimates.__getitem__)
        min_estimate = self.estimates.pop(lowest)
        del self.errors[lowest]
        # when an element gets evicted, its history is lost. untracked els 
        # can have a true sum between 0 and min_estimate, so set the error 
        # bound for the worst case - min_estimate
        self.estimates[el] = min_estimate + val 
        self.errors[el] = min_estimate

    
    def topk(self, k: int):
        return sorted(self.estimates.items(), key=lambda x: -x[1])[:k]