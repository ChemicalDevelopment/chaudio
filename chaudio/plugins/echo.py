"""

takes input, adds white noise

"""

from chaudio.source import Source
from chaudio.plugins import Basic

# echos the input (not the same as reverb)
class Echo(Basic):
    def process(self, _data):
        data = Source(_data)
        res = data.copy()

        # delay, in seconds
        delay = self.getarg("delay", 0)
        # initial delay, in seconds
        idelay = self.getarg("idelay", 0)
        # how many repeats should we calculate
        num = self.getarg("num", 16)
        # amplitude of all echos
        amp = self.getarg("amp", .52)
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
