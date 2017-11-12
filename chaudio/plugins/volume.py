"""

A simple multiplier to scale the volume

"""

from chaudio.source import Source
from chaudio.plugins import Basic

class Volume(Basic):
    """

    A simple multiplier to scale the volume. This is effectively the same thing as ``kwargs["amp"] * _data``, but being a plugin, it is compatable with other libraries. 

    """    
    def process(self, _data):
        """Returns the result, but amplified

        Kwargs
        ------

        :"amp": The amplitude to multiply the source by


        """
        return self.getarg("amp", 1.0) * Source(_data)

