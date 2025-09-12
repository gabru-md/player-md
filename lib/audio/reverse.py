import numpy as np
from pygame import sndarray

from lib.audio.plugin import AudioPlugin


class ReversePlugin(AudioPlugin):

    def process_sound(self, sound):
        samples = sndarray.array(sound)
        reversed_samples = samples[::-1]
        # Ensure the array is C-contiguous before creating the sound object
        reversed_samples_contiguous = np.ascontiguousarray(reversed_samples)

        # Use sndarray.make_sound() with the contiguous array
        reversed_sound = sndarray.make_sound(reversed_samples_contiguous)

        return reversed_sound