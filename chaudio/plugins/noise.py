"""

adds white noise to input

"""

from chaudio.source import Source
from chaudio.util import times
from chaudio.plugins import Basic
from chaudio.waves import noise

class Noise(Basic):
    """

    adds white noise to input

    """    
    def process(self, _data):
        """Returns the result, with white noise added

        Kwargs
        ------

        :"amp": The amplitude of the whitenoise

        """
        data = Source(_data)
        return data + self.getarg("amp", 1.0) * noise(times(data))

