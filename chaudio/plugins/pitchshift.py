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
        n = self.getarg("n", 2048*4)
        chunker = FFTChunker(_data, n=n, hop=self.getarg("hop", n // 4))
        cents = self.getarg("cents", 0)

        res = chaudio.Source(_data).cleared()

        ct = 0
        last_chunk = None

        output_chunks = []

        stretch_factor = transpose(1, -cents)

        for chunk in chunker.chunks():
            #t = chunker.chunk_time_offset(ct) + chaudio.times(chunk.chunk_time(ct), chunker.audio.hz)

            fchunk = chunker.fft_chunk(chunk)
            #fchunk = chunker.fft_chunk(np.hanning(len(chunk)) * chunk)

            if ct != 0:
                """
                last_chunk = output_chunks[-1]

                phase_shift = np.angle(fchunk) - np.angle(last_chunk)

                freq_dev = (phase_shift / (chunker.hop / chunker.audio.hz)) - chunker.domain()

                true_freq = chunker.domain() + (freq_dev + np.pi) % (2 * np.pi) - np.pi

                new_phase = np.angle(last_chunk) + (((chunker.hop / transpose(1, cents)) / chunker.audio.hz) * true_freq)

                new_mag = np.abs(chaudio.util.map_domain(chunker.domain(), fchunk, lambda hz: transpose(hz, cents)))

                fchunk = new_mag * (np.cos(new_phase) + 1j * np.sin(new_phase))

                """
                new_phase = np.real(chaudio.util.map_domain(chunker.domain(), np.angle(fchunk), lambda hz: transpose(hz, cents)))

                for i in range(0, len(new_phase)):
                    new_phase[i] = (new_phase[i] + np.pi) % (2 * np.pi) - np.pi

                new_mag = np.abs(chaudio.util.map_domain(chunker.domain(), fchunk, lambda hz: transpose(hz, cents)))

                rchunk = []

                for i in range(0, len(fchunk)):
                    rchunk += [new_mag[i] * (np.cos(new_phase[i]) + 1j * np.sin(new_phase[i]))]

                fchunk = rchunk

                #nchunk = chaudio.util.map_domain(chunker.domain(), chunk, lambda hz: transpose(hz, cents))

            output_chunks += [fchunk]

            #output_chunks += [nchunk]
            ct += 1

        ct = 0
        res.ensure(chunker.hop * len(chunker) + chunker.n)
        
        #print (res.samples)
        for chunk in output_chunks:
            ichunk = chunker.ifft_chunk(chunk)
            for i in range(0, len(ichunk)):
                ichunk[i] = ichunk[i][:chunker.hop]
                #coff = int(ct * chunker.hop / transpose(1, cents))
                coff = int(ct * chunker.hop)
                res[i][coff:coff + len(ichunk[i])] = ichunk[i]
            """
            for i in range(0, len(chunk)):
                #cres = np.hanning(len(ichunk[i])) * ichunk[i]
                cres = ichunk[i]
                res[i,chunker.hop * ct:chunker.hop * ct + len(cres)] = cres
            """
            ct += 1

        #mapped_domain = chunker.fft_map_domain(chunker.fft_chunks(chunker.chunks()), lambda t, freq: transpose(freq, cents))

        return res
        
