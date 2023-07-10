import MSPhotomAnalysis as msp
import numpy as np
import PIL.Image as img
from dataclasses import dataclass

# Test functions for parts of the MSPhotomAnalysis.py file
traces = []
for i in range(10): traces.append(np.arange(30))



@dataclass
class data():
    channels: int = 2

d = data()

print(d.channels)