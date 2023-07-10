import MSPhotomAnalysis as msp
import numpy as np
import PIL.Image as img

# Test functions for parts of the MSPhotomAnalysis.py file
traces = []
for i in range(10): traces.append(np.arange(30))

traces = msp.splittraces(traces,2)
print(traces[0])
traces = msp.reshapetraces(traces,3)

print(traces[0])