# topkstream

It's straightforward solve for top-k elements in a running data stream.  I was interested in extracting the top-k elements in a data stream for any time window, specifically top-k elements by sum (assuming high cardinality). 

To approach this, I implemented 2 approaches: 
1. (Assuming values in the stream have weight/count = 1) Space-Saving: https://www.cse.ust.hk/~raywong/comp5331/References/EfficientComputationOfFrequentAndTop-kElementsInDataStreams.pdf

https://dimacs.rutgers.edu/~graham/pubs/papers/freq.pdf
https://www.cs.uml.edu/~ge/pdf/icde17_topkFreq.pdf
