"""

pitch shifts

"""

from chaudio.util import FFTChunker, transpose
from chaudio.plugins import Basic
import chaudio
import numpy as np

class PitchShift(Basic):
    """

    shifts pitch, without affecting speed

    """    
    def process(self, _data):
        """Returns the result, with white noise added

        Kwargs
        ------

        :"chunk_s": FFT chunk size, in seconds

        :"cents": cents to transpose

        """
        n = self.getarg("n", 1024*4)
        chunker = FFTChunker(_data, n=n, hop=self.getarg("hop", n // 4))
        cents = self.getarg("cents", 0)

        res = chaudio.Source(_data).cleared()

        ct = 0
        last_chunk = None

        output_chunks = []

        stretch_factor = transpose(1, -cents)

        domain = chunker.domain()

        samples_done = 0

        for ct, chunk in enumerate(chunker.chunks()):
            #t = chunker.chunk_time_offset(ct) + chaudio.times(chunk.chunk_time(ct), chunker.audio.hz)
            
            t = samples_done / res.hz

            fchunk = chunker.fft_chunk(chunk)

            rchunk = np.zeros_like(fchunk)

            for ch in range(len(fchunk)):

                from_i = np.array(range(len(domain))) * stretch_factor
                from_i, tmp = from_i.astype(np.int), from_i % 1.0

                condition = (from_i < len(fchunk[ch]) - 1) & (from_i >= 0)

                cur_phase = np.angle(fchunk[ch])
                new_phase = (t * (1 - stretch_factor) + cur_phase) / stretch_factor
                #new_phase = cur_phase

                mag = np.abs(fchunk[ch])

                fchunk[ch] = mag * np.exp(1j * new_phase)

                goodvals = np.where(condition)
                badvals = np.where(~condition)
                
                a = np.zeros_like(fchunk[ch])
                b = np.zeros_like(fchunk[ch])

                a[badvals] = 0
                b[badvals] = 0

                a[goodvals] = fchunk[ch][goodvals]
                b[goodvals] = np.roll(fchunk[ch], 1)[goodvals]

                rchunk[ch] = (1.0 - tmp) * a + (tmp) * b

            output_chunks += [rchunk]

            ct += 1

            samples_done += len(chunk[0])

        ct = 0
        res.ensure(chunker.hop * len(chunker) + chunker.n)
        
        for chunk in output_chunks:
            ichunk = chunker.ifft_chunk(chunk)
            for i in range(0, len(ichunk)):
                ichunk[i] = ichunk[i][:chunker.hop]
                coff = int(ct * chunker.hop)
                res[i][coff:coff + len(ichunk[i])] = ichunk[i]
            ct += 1

        return res
        
