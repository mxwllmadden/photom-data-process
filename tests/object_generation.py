# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:39:53 2024

@author: mbmad
"""

import numpy as np
from matplotlib import pyplot as pp
from itertools import product
from math import sin


def create_test_image(func_array, imgnum):
    vals = [func(imgnum) for func in func_array]
    img = np.zeros((424,424), dtype=np.uint16)
    ranges = [(0,140),
              (142,282),
              (284,424)]
    for val, (yrange, xrange) in zip(vals, product(ranges,ranges)):
        img[yrange[0]:yrange[1],xrange[0]:xrange[1]] = val
        print(xrange,yrange)
    return img
    
pp.imshow(create_test_image([lambda x : 10,
                             lambda x : 20,
                             lambda x : 40,
                             lambda x : sin(x/100),
                             lambda x : x], 1), cmap='binary')
    