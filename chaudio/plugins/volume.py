"""

multiplies the source by a factor

"""

from chaudio.source import Source
from chaudio.plugins import Basic

class Volume(Basic):
    def process(self, _data):
        return self.getarg("amp", 1.0) * Source(_data)

