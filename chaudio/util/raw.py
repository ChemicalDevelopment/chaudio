"""

raw utils, returns raw arrays

"""

import chaudio
import numpy as np

# returns time arrays. if v is an array
def times(v, hz=None):
    t = None
    if hz is None:
        if issubclass(type(v), chaudio.source.Source):
            hz = v.hz
            t = v.seconds
        elif type(v) is np.ndarray:
            hz = chaudio.defaults["hz"]
            t = len(v) / hz
        else:
            hz = chaudio.defaults["hz"]

    if t is None:
        t = v

    return np.arange(0, t, 1.0 / hz)

#
def normalize_factor(v):
    if issubclass(type(v), chaudio.source.Source):
        return max([normalize_factor(i) for i in v.data])
    elif type(v) is np.ndarray:
        return np.max(np.abs(v))
    else:
        raise Exception("don't know how to normalize '%s'" % type(v).__name__)

# returns a normalized vector
def normalize(v):
    fact = normalize_factor(v)
    if fact == 0:
        return v
    else:
        return v / fact

