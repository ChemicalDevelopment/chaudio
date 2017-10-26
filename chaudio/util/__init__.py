"""

this module is for utility functions:

raw.py contains utilities for operating on straight data arrays (mono np arrays), frequencies, etc

io.py is for input output (files, strings)

this file is for major utils, and typically applies to a chaudio.Source, or generics

"""

from chaudio.util import raw
from chaudio.util import io
import chaudio

import numpy as np

# returns a single audio. This will sound weird with multiple channels
def flatten(audio):
    return chaudio.Source(audio).flatten()

# returns the normalization factor (the range of values) for dtype
def norm_factor(dtype):
    if dtype in (float, np.float32):
        return 1.0
    elif dtype in (np.int8, ):
        return 2.0 ** 7 - 1.0
    elif dtype in (int, np.int16):
        return 2.0 ** 15 - 1.0
    elif dtype in (np.int32, ):
        return 2.0 ** 31 - 1.0
    else:
        raise Exception("unknown dtype %s" % (dtype, ))
        return 1.0


