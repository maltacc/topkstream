# Top-K Streamer

It's straightforward solve for top-k elements in a running data stream.  I was interested in extracting the top-k elements in a data stream for any time window, specifically top-k elements by sum (assuming high cardinality). 

To approach this, I implemented 2 algorithms: 
### 1. Space-Saving
**Reference:** https://www.cse.ust.hk/~raywong/comp5331/References/EfficientComputationOfFrequentAndTop-kElementsInDataStreams.pdf

(Assuming values in the stream have weight/count = 1) : Estimate the frequencies of elements by monitoring m elements at a time, incrementing an element's counter as it's observed in the stream. Using linked lists, each counter points to a parent bucket, and parent buckets are in sorted order; this offers $\Theta$(1) time retrieval.

#### To run the visualizer: ```open visualization.html```

![screenshot](./assets/ss-algo.png)

https://dimacs.rutgers.edu/~graham/pubs/papers/freq.pdf
https://www.cs.uml.edu/~ge/pdf/icde17_topkFreq.pdf
