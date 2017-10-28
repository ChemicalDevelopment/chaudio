"""

takes input, adds white noise

"""

from chaudio.source import Source
from chaudio.util import times
from chaudio.plugins import Basic
from chaudio.waves import noise

class Noise(Basic):
    def process(self, _data):
        data = Source(_data)
        return data + self.getarg("amp", 1.0) * noise(times(data), -1)

