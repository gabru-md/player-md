import pygame
import numpy as np
import io
import wave

class Equalizer:
    """
    A simple single-band audio equalizer that processes Pygame Sound objects.

    This class applies a single second-order band-pass filter to the audio data.
    It's implemented without external libraries like SciPy, making it simpler
    to understand and use.
    """

    def __init__(self, center_frequency=170, q_factor=1.0, gain_db=0.0):
        """
        Initializes the equalizer with a single configurable band.

        Args:
            center_frequency (float): The center frequency of the band in Hz.
            q_factor (float): The quality factor of the filter. A higher Q means a
                              narrower band.
            gain_db (float): The gain in decibels. Positive for boost, negative for cut.
        """
        self.center_frequency = center_frequency
        self.q_factor = q_factor
        self.gain_db = gain_db
        self.b = None
        self.a = None

    def _design_filter(self):
        """
        Manually designs a second-order band-pass filter.

        This function calculates the filter coefficients (b and a arrays)
        based on the provided center frequency, Q factor, and gain.
        """

        if self.a is None and self.b is None:
            # Convert frequency to radians per sample
            sample_rate = pygame.mixer.get_init()[0]
            omega = 2 * np.pi * self.center_frequency / sample_rate

            # Calculate filter coefficients
            alpha = np.sin(omega) / (2 * self.q_factor)
            gain_lin = 10 ** (self.gain_db / 20.0)

            # Numerator coefficients (b)
            b0 = alpha
            b1 = 0
            b2 = -alpha

            # Denominator coefficients (a)
            a0 = 1 + alpha
            a1 = -2 * np.cos(omega)
            a2 = 1 - alpha

            # Apply gain to the numerator
            b = np.array([b0, b1, b2]) * gain_lin
            a = np.array([a0, a1, a2])

            self.b = b
            self.a = a

    def process_sound(self, sound):
        """
        Applies the equalization to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be processed.

        Returns:
            pygame.mixer.Sound: A new, equalized Sound object.
        """

        self._design_filter()
        raw_data = sound.get_raw()
        samples = np.frombuffer(raw_data, dtype=np.int16)

        # Convert to float for processing and normalize
        processed_samples = samples.astype(np.float32)

        # Simple manual IIR filter implementation.
        # This is a basic form of the lfilter function from scipy.
        y = np.zeros_like(processed_samples)
        for n in range(len(processed_samples)):
            x_n = processed_samples[n]
            y_n_minus_1 = y[n - 1] if n > 0 else 0
            y_n_minus_2 = y[n - 2] if n > 1 else 0

            y[n] = (self.b[0] * x_n + self.b[1] * processed_samples[n - 1] + self.b[2] * processed_samples[n - 2]
                    - self.a[1] * y_n_minus_1 - self.a[2] * y_n_minus_2) / self.a[0]

        # Convert back to 16-bit integer and ensure values are within range
        processed_samples = np.clip(y, -32768, 32767).astype(np.int16)

        return pygame.mixer.Sound(processed_samples.tobytes())
