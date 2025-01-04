import numpy as np
from scipy.spatial import cKDTree
#import matplotlib.pyplot as plt

def box_counting(points, box_sizes):
    counts = []
    for size in box_sizes:
        boxes = np.floor(points / size).astype(int)
        unique_boxes = np.unique(boxes, axis=0)
        counts.append(len(unique_boxes))
    return counts

def fractal_dimension(points, box_sizes=np.logspace(-4, 0, 30)):
    counts = box_counting(points, box_sizes)
    coeffs = np.polyfit(np.log(box_sizes), np.log(counts), 1)
    return -coeffs[0]