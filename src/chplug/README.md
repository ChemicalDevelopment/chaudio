# chplug

`chplug` is a way to design plugins in a simple language, such that compilation is not needed (and `chaudio` development library doesn't have to be installed).



## Specification

To create a simple gain plugin, create a file `gain.chplug`:

```
int @channels;
int @sampleRate;

(int channels, int sampleRate) init {
    @channels = channels;
    @sampleRate = sampleRate;
}

(double* in, double* out, int N) process {
    int i, j;
    for (i = 0; i < N; i++) {
        for (j = 0; j < @channels; j++) {
            out[@channels * i + j] = in[@channels * i + j];
        }
    }
}

() free {
    # do nothing
}

```


