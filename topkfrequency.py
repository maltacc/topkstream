# Implementation of Metwally et al.'s space-saving algorithm 
# from "Efficient Computation of Frequent and Top-k Elements in Data Streams"

import string
from typing import List 
from collections import defaultdict
import random
from collections import Counter as ExactCounter

class _Bucket: 
    __slots__ = ("val", "child", "prev", "next")
    def __init__(self, val: int): 
        self.val = val
        self.child = None # start of children counter LL
        self.prev = self.next = None

class _Counter: 
    __slots__ = ("el", "bkt", "error", "prev", "next")

    def __init__(self, el: str, bkt: _Bucket, err: int): 
        self.el = el
        self.bkt = bkt
        self.error = err
        self.prev = self.next = None

class SpaceSaving: 

    def __init__(self, capacity: int): 
        self.bkts = _Bucket(0) # bucket -> DLL
        self.cap = capacity
        self.mp = defaultdict(_Counter) # string -> counter

    @staticmethod
    def _removeElFromBucket(el: _Counter): 
        bkt = el.bkt
        prev, fwd = el.prev, el.next 
        if prev: 
            prev.next = fwd
        else: 
            bkt.child = fwd

        if fwd:
            fwd.prev = prev
        prev = fwd = None

    @staticmethod
    def _addElToBucket(el: _Counter, bkt: _Bucket):
        el.bkt = bkt
        el.prev = None 
        el.next = bkt.child
        if bkt.child:
            bkt.child.prev = el
        bkt.child = el

    def _moveToBucket(self, el: _Counter, nb: _Bucket): 
        self._removeElFromBucket(el)
        self._addElToBucket(el, nb)
    
    def _deleteBucket(self, bkt: _Bucket):
        prev, fwd = bkt.prev, bkt.next 
        prev.next = fwd
        if fwd:
            fwd.prev = prev

    def _insertBucketAfter(self, val: int, prevBkt: _Bucket) -> _Bucket:
        newBkt = _Bucket(val)
        fwd = prevBkt.next
        prevBkt.next = newBkt
        newBkt.prev = prevBkt
        newBkt.next = fwd
        if fwd:
            fwd.prev = newBkt
        return newBkt

    def _updateElement(self, el: _Counter): 
        bkt = el.bkt 
        fwd = bkt.next
        target = bkt.val + 1
        if fwd and fwd.val == target: 
            target = fwd
        else: 
            target = self._insertBucketAfter(target, bkt)
        self._removeElFromBucket(el)
        self._addElToBucket(el, target)

        # if bucket is empty, remove it 
        if bkt is not self.bkts and bkt.child is None: 
            self._deleteBucket(bkt)

    def offer(self, el: str):
        # add element to stream
        if el in self.mp:
            self._updateElement(self.mp[el])
            return 
        
        if len(self.mp) < self.cap: 
            # can add element 
            head = self.bkts 
            first = head.next 
            if first and first.val == 1: 
                bkt = first
            else: 
                bkt = self._insertBucketAfter(1, head)
            newEl = _Counter(el, bkt, 0)
            self._addElToBucket(newEl, bkt)
            self.mp[el] = newEl
            return 
        
        # evict lowest element 
        lowest = self.bkts.next.child
        del self.mp[lowest.el]
        lowest.el = el
        lowest.error = lowest.bkt.val
        self.mp[el] = lowest
        self._updateElement(lowest)
        
    def topk(self, k: int) -> List[int]: 
        res = []

        bkt = self.bkts 
        while bkt.next: 
            bkt = bkt.next 
        
        while bkt is not self.bkts and len(res) < k:
            el = bkt.child
            while el and len(res) < k: 
                res.append((el.el, bkt.val, el.error))
                el = el.next
            bkt = bkt.prev
        return res
    

if __name__ == "__main__": 
    random.seed(7)
    universe = [f"S{i}" for i in range(1000)]
    weights = [1.0 / (i + 1) for i in range(len(universe))]  # Zipf-ish skew
 
    N = 200000
    ss = SpaceSaving(capacity=50)
    exact = ExactCounter()
    for _ in range(N):
        x = random.choices(universe, weights=weights)[0]
        ss.offer(x)
        exact[x] += 1
 
    true_top = [el for el, _ in exact.most_common(10)]
    print(f"Stream: {N} events, 1000 symbols, {ss.cap} counters\n")
    print("rank  element   true     est    error   true in [est-err, est]?")
    all_ok = True

    for rank, (el, est, err) in enumerate(ss.topk(10), 1):
        true = exact[el]
        ok = est - err <= true <= est
        all_ok &= ok
        print(f"{rank:>3}   {el:>6}   {true:>6}  {est:>6}  {err:>5}   {ok}")
 
    recovered = [el for el, _, _ in ss.topk(10)]
    print(f"\ntop-10 recovered exactly: {recovered == true_top}")
    print(f"all error bounds held:    {all_ok}")