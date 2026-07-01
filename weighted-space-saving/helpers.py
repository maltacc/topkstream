from weighted_space_saving import WeightedSpaceSaving

def merge(a: 'WeightedSpaceSaving', b: 'WeightedSpaceSaving', capacity: int):
    res = {} 

    # assume sketches have non-overlapping intervals 
    a_min = a.min_estimate
    b_min = b.min_estimate
    for el in set(a.estimates) | set(b.estimates):
        est = a.estimates.get(el, 0) + b.estimates.get(el, 0)
        # true value could be from 0 - min_estimate
        err = (a.errors.get(el, a_min) + b.errors.get(el, b_min))
        res[el] = (est, err)

    # keep top <capacity> elements 
    ans = WeightedSpaceSaving(capacity=capacity)
    for el, (est, err) in sorted(res.items(), key=lambda x: -x[1][0])[:capacity]: 
        ans.estimates[el] = est
        ans.errors[el] = err
    return ans
