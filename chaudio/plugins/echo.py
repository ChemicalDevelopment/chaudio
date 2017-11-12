"""

Adds in the echo effect, with each successive echo being decayed.

"""

from chaudio.source import Source
from chaudio.plugins import Basic

class Echo(Basic):
    """

    Adds in the echo effect, with each successive echo being decayed.

    """

    def process(self, _data):
        """Returns the result, but echoed

        So, the the amplitude of the ``n`` th echo is ``kwargs["amp"] * (n) ** kwargs["decay"]``

        Kwargs
        ------

        :"idelay": The initial delay, in seconds, before the echos begin at all
        :"delay": The delay for each successive echo
        :"num": How many echos to factor in
        :"amp": The base amplitude of all echos
        :"decay": The multiplication of the signal each successive echo

        """

        data = Source(_data)
        res = data.copy()

        # initial delay, in seconds
        idelay = self.getarg("idelay", 0)
        # delay, in seconds
        delay = self.getarg("delay", .15)
        # how many repeats should we calculate
        num = self.getarg("num", 8)
        # amplitude of all echos
        amp = self.getarg("amp", .9)
        # decay of each iteration (multiplicative)
        decay = self.getarg("decay", .56)

        # keep track of the current echo value
        cur_echo = amp * res

        # add 'num' echos, each time the strength multiplied by 'decay'
        for i in range(1, num+1):
            res.insert(int(data.hz * (idelay + delay * i)), cur_echo)
            # decay signal
            cur_echo *= decay

        # return our result
        return res
