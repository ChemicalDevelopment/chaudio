"""Visually Representing Data (:mod:`chaudio.visuals`)
==============================================

.. currentmodule:: chaudio.visuals

All sorts of visualization code

"""

import chaudio
import numpy as np
import time
import os
import subprocess
import tempfile


try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib.ticker as ticker
except ImportError:
    pass


def graph(audio, title="Audio Amplitude Graph", label=None):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import matplotlib.ticker as ticker
    except ImportError:
        chaudio.msgprint("Error, cannot use 'chaudio.visuals' without installing package 'matplotlib'")
        chaudio.msgprint("  Try: 'pip3 install matplotlib'")

    to_graph = chaudio.source.Source(audio)
    t = chaudio.times(to_graph)
    
    if isinstance(label, tuple) or isinstance(label, list):
        if len(label) != to_graph.channels:
            chaudio.msgprint("Error: gave labels as a tuple: %s, but the length != the number of channels (err: %d != %d)" % (label, len(label), to_graph.channels))
            exit()

    for i in range(0, to_graph.channels):
        plt.subplot(to_graph.channels, 1, i + 1)
        plt.plot(t, to_graph[i], linewidth=1)
        _yl = 'Channel %d' % i
        if i == 0:
            _yl += " (L)"
        elif i == 1:
            _yl += " (R)"
        if i == 0:
            plt.title(title)
        if label:
            if isinstance(label, tuple) or isinstance(label, list):
                plt.ylabel(label[i])
            else:
                plt.ylabel(label)
        else:
            plt.ylabel(_yl)

    plt.show()


class Oscilliscope(object):

    def __init__(self, data, window_time=.12, sync=None, sync_time=None, fps=24, audio_playback=True, _insert_time=0, playback_speed=1.0):
        if sync_time is None:
            sync_time = window_time / 4.0
        self.y_data = chaudio.source.Mono(data)
        self._insert_time = _insert_time
        self.y_data.prepend(np.zeros(int(self._insert_time * self.y_data.hz)))
        self.window_time = window_time
        self.sync = sync
        self.sync_time = sync_time
        self.audio_playback = audio_playback
        self.fps = fps
        self.playback_speed = playback_speed
        self.fig, self.ax = plt.subplots()
        self.ax.grid(False)

        self.__is_live = True
        self.anim = animation.FuncAnimation(self.fig, self.run_anim, blit=False, interval=1000//self.fps, repeat=False, init_func=self.anim_init, save_count=int(self.y_data.seconds * self.fps))
        #self.anim = animation.FuncAnimation(self.fig, self.run_anim, self.data_gen, blit=False, interval=50, repeat=False, init_func=self.anim_init, save_count=int(self.y_data.seconds * self.fps))

    def show(self):
        self.__is_live = True
        self.show_time = time.time()
        if self.audio_playback:
            playback = chaudio.play(self.y_data)

        def handle_close(evt):
            playback.stop()

        self.fig.canvas.mpl_connect('close_event', handle_close)
        plt.show()

    def anim_init(self):
        self.line, = self.ax.plot([], [], lw=2)
        return self.line,

    def save(self, *args, **kwargs):
        if self.audio_playback:
            FNULL = open(os.devnull, 'w')
            if subprocess.call([plt.rcParams['animation.ffmpeg_path'], '-h'], stdout=FNULL, stderr=FNULL) != 0:
                do_audio_playback = False
                chaudio.msgprint("warning: 'ffmpeg' support not found. Please install ffmpeg, or ensure that the 'ffmpeg' binary is on your PATH")
            else:
                do_audio_playback = True
                args = list(args)
                output_file = args[0]
                args[0] = tempfile.mkstemp(prefix='chaudio_video_tmp', suffix=os.path.splitext(output_file)[1])[1]
                args = tuple(args)
            FNULL.close()

        if "fps" not in kwargs:
            kwargs["fps"] = self.fps
        if "writer" not in kwargs:
            _, ext = os.path.splitext(args[0])
            if ext.lower() == ".gif":
                kwargs["writer"] = "imagemagick"
            else:
                Writer = animation.writers['ffmpeg']
                kwargs["writer"] = Writer(fps=kwargs["fps"])

        del kwargs["fps"]

        self.__is_live = False

        self.anim.save(*args, **kwargs)


        if do_audio_playback:
            audio_file = tempfile.mkstemp(prefix='chaudio_playback_tmp', suffix='.wav')[1]

            chaudio.tofile(audio_file, self.y_data, silent=True)

            #ffmpeg -i graph.mp4 -i sound.wav -c:v copy -c:a aac -strict experimental output.mp4 -y

            FNULL = open(os.devnull, 'w')

            rcode = subprocess.call([plt.rcParams['animation.ffmpeg_path'], 
                '-i', args[0], 
                '-i', audio_file, 
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-strict', 'experimental',
                output_file,
                '-y'
            ], stdout=FNULL, stderr=FNULL)
            FNULL.close()

            if rcode != 0:
                chaudio.msgprint("warning: ffmpeg code was non-zero (got %d)" % rcode)

            os.remove(args[0])

        chaudio.msgprint("wrote to file %s" % output_file)


    def data_gen_specific(self, t, _samples):
        sample_offset = int(t * self.y_data.hz)
        samples = _samples // 2

        if sample_offset - samples > len(self.y_data[0]):
            return None

        # handle cases that contain values out of range (set them to 0)
        if sample_offset + samples > len(self.y_data[0]):
            available = self.y_data[0][sample_offset - samples:]
            return np.append(available, np.zeros(2 * samples - len(available)))
        elif sample_offset - samples < 0:
            available = self.y_data[0][:sample_offset + samples]
            return np.append(np.zeros(2 * samples - len(available)), available)
        else:
            return self.y_data[0][sample_offset - samples:sample_offset + samples]

    def run_anim(self, frame):
        t_offset = float(frame + 1) / self.fps

        if self.__is_live:
            t_offset = time.time() - self.show_time

        # 2 is for sync figure
        samples = 2 * int(self.y_data.hz * (self.window_time + self.sync_time))

        y = self.data_gen_specific(t_offset, samples)

        if y is None:
            return

        t_arr = np.arange(t_offset - samples / self.y_data.hz, t_offset + samples / self.y_data.hz, 1.0 / self.y_data.hz)

        sind = len(y) // 4
        window_samples = int(self.y_data.hz * self.window_time)
        sync_samples = int(self.y_data.hz * self.sync_time)

        if self.sync:
            if self.sync == "left":
                for i in range(len(y) // 4, len(y) // 4 + sync_samples):
                    if y[i] <= 0 and y[i+1] >= 0:
                        sind = i
                        break
            elif self.sync == "center":
                for i in range(len(y) // 2, len(y) // 2 + sync_samples):
                    if y[i] <= 0 and y[i+1] >= 0:
                        sind = i - len(y) // 4
                        break
            elif self.sync == "right":
                for i in range(3 * len(y) // 2, 3 * len(y) // 2 + sync_samples):
                    if y[i] <= 0 and y[i+1] >= 0:
                        sind = i - len(y) // 2
                        break
            else:
                chaudio.msgprint("Error, unexpected sync value: '%s'" % self.sync)
                exit()

        t_arr = t_arr[sind:sind+window_samples]
        y = y[sind:sind+window_samples]

        xmin, xmax = t_arr[0], t_arr[-1]

        self.ax.set_xlim(xmin, xmax)

        ymin, ymax = np.min(self.y_data[0]), np.max(self.y_data[0])
        dc_offset = (ymax + ymin) / 2.0

        self.ax.set_ylim(2 * (dc_offset - 1.1 * ymax / 2.0), 2 * (dc_offset - 1.1 * ymin / 2.0))

        self.ax.xaxis.set_ticks(np.linspace(xmin, xmax, 5))

        self.ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        self.ax.figure.canvas.draw()

        self.line.set_data(t_arr, y)

        return self.line,


#Writer = animation.writers['ffmpeg']
#writer = Writer(fps=24, metadata=dict(artist='Me'), bitrate=1800)

#ani.save('lines.gif', writer='imagemagick', fps=60)

#ani.save('lines.mp4', writer='ffmpeg', fps=60)


#plt.show()


def oscilliscope(audio):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        import matplotlib.ticker as ticker
    except ImportError:
        chaudio.msgprint("Error, cannot use 'chaudio.visuals' without installing package 'matplotlib'")
        chaudio.msgprint("  Try: 'pip3 install matplotlib'")

    to_graph = chaudio.source.Source(audio)



