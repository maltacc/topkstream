import random
from collections import defaultdict
from weighted_space_saving import WeightedSpaceSaving
from helpers import merge
from merge_tree import MergeTree


# --- WeightedSpaceSaving ---

def test_basic_topk():
    ss = WeightedSpaceSaving(capacity=3)
    ss.offer("a", 10)
    ss.offer("b", 5)
    ss.offer("c", 8)
    assert ss.topk(2) == [("a", 10), ("c", 8)]

def test_eviction_sets_error():
    ss = WeightedSpaceSaving(capacity=2)
    ss.offer("a", 10)
    ss.offer("b", 5)
    ss.offer("c", 1)  # evicts "b" (min=5), c gets estimate=6, error=5
    assert ss.estimates["c"] == 6
    assert ss.errors["c"] == 5

def test_error_bound_holds():
    random.seed(42)
    ss = WeightedSpaceSaving(capacity=10)
    true_sums = defaultdict(float)
    elements = [f"e{i}" for i in range(15)]
    for _ in range(1000):
        el = random.choice(elements)
        val = random.random()
        ss.offer(el, val)
        true_sums[el] += val
    for el, est in ss.estimates.items():
        assert true_sums[el] <= est + 1e-9, f"{el}: true={true_sums[el]:.4f}, est={est:.4f}"


# --- merge ---

def test_merge_sums_estimates():
    a = WeightedSpaceSaving(capacity=5)
    a.offer("x", 10)
    b = WeightedSpaceSaving(capacity=5)
    b.offer("x", 7)
    m = merge(a, b, capacity=5)
    assert m.estimates["x"] == 17

def test_merge_absent_element_uses_min_estimate():
    a = WeightedSpaceSaving(capacity=2)
    a.offer("x", 10)
    a.offer("y", 3)   # min_estimate = 3
    b = WeightedSpaceSaving(capacity=2)
    b.offer("z", 5)
    m = merge(a, b, capacity=5)
    # "z" absent from a: error contribution = a.min_estimate = 3
    assert m.errors["z"] == a.min_estimate + b.errors.get("z", b.min_estimate)

def test_merge_capacity_respected():
    a = WeightedSpaceSaving(capacity=5)
    b = WeightedSpaceSaving(capacity=5)
    for i in range(5):
        a.offer(f"a{i}", i + 1)
        b.offer(f"b{i}", i + 1)
    m = merge(a, b, capacity=5)
    assert len(m.estimates) <= 5


# --- MergeTree end-to-end oracle ---

def brute_force_topk(events, t1, t2, k):
    sums = defaultdict(float)
    for t, el, val in events:
        if t1 <= t < t2:
            sums[el] += val
    return sorted(sums.items(), key=lambda x: -x[1])[:k]

def test_end_to_end():
    random.seed(0)
    dur = 10
    mt = MergeTree(capacity=20, dur=dur)
    events = []
    for t in range(200):
        el = random.choice(["a", "b", "c", "d", "e", "f"])
        val = random.uniform(1, 10)
        events.append((t, el, val))
        mt.offer(t, el, val)
    mt.offer(300, "__sentinel__", 0)  # flush current epoch

    for t1, t2 in [(0, 50), (10, 100), (50, 150), (0, 200)]:
        exact = dict(brute_force_topk(events, t1, t2, k=6))
        approx = dict(mt.query(t1, t2, k=6))
        for el, true_sum in exact.items():
            if el in approx:
                assert approx[el] >= true_sum - 1e-9, \
                    f"[{t1},{t2}] {el}: est={approx[el]:.4f} < true={true_sum:.4f}"


# --- Regression tests for fixed bugs ---

def test_cur_not_shared_across_epochs():
    mt = MergeTree(capacity=5, dur=10)
    mt.offer(0, "a", 100)   # epoch 0
    mt.offer(10, "b", 50)   # epoch 1 — closes epoch 0
    mt.offer(20, "__", 0)   # epoch 2 — closes epoch 1

    result = dict(mt.query(0, 10, k=5))
    assert "b" not in result, "epoch 1 data bled into epoch 0's sketch"

def test_no_double_counting():
    mt = MergeTree(capacity=5, dur=10)
    for t in range(20):
        mt.offer(t, "x", 1)
    mt.offer(20, "__", 0)   # close epoch 1

    result = dict(mt.query(0, 10, k=1))
    assert abs(result.get("x", 0) - 10) < 1e-9, \
        f"double-counted: got {result.get('x')}, expected 10"

def test_empty_query_returns_empty():
    mt = MergeTree(capacity=5, dur=10)
    assert mt.query(100, 200, k=5) == []


if __name__ == "__main__":
    tests = [
        test_basic_topk,
        test_eviction_sets_error,
        test_error_bound_holds,
        test_merge_sums_estimates,
        test_merge_absent_element_uses_min_estimate,
        test_merge_capacity_respected,
        test_end_to_end,
        test_cur_not_shared_across_epochs,
        test_no_double_counting,
        test_empty_query_returns_empty,
    ]
    for t in tests:
        t()
        print(f"  PASS  {t.__name__}")
