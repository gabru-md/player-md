import pygame
import pygame.sndarray as sndarray
import numpy as np

from lib.audio.plugin import AudioPlugin


class Equalizer(AudioPlugin):
    """
    A robust single-band audio equalizer that processes Pygame Sound objects.

    This class applies a single second-order band-pass filter to audio data
    using safe sndarray operations to avoid byte conversion errors.
    """

    def __init__(self, center_frequency=170, q_factor=1.0, gain_db=0.0):
        """
        Initialize the equalizer with a single configurable band.

        Args:
            center_frequency (float): Center frequency of the band in Hz
            q_factor (float): Quality factor - higher Q means narrower band
            gain_db (float): Gain in decibels (positive boost, negative cut)
        """
        self.center_frequency = center_frequency
        self.q_factor = q_factor
        self.gain_db = gain_db
        self.b = None
        self.a = None

        # Filter memory for each channel (stereo support)
        self.x_history = {}  # Input history
        self.y_history = {}  # Output history

    def _design_filter(self):
        """
        Design a second-order peaking EQ filter.

        Uses a peaking filter design which is more suitable for EQ than bandpass.
        """
        if self.a is None or self.b is None:
            sample_rate = pygame.mixer.get_init()[0]
            if sample_rate is None:
                raise RuntimeError("Pygame mixer not initialized")

            # Convert to normalized frequency
            omega = 2 * np.pi * self.center_frequency / sample_rate

            # Calculate filter coefficients for peaking EQ
            A = 10 ** (self.gain_db / 40.0)  # Linear gain
            alpha = np.sin(omega) / (2 * self.q_factor)

            # Peaking EQ coefficients
            b0 = 1 + alpha * A
            b1 = -2 * np.cos(omega)
            b2 = 1 - alpha * A

            a0 = 1 + alpha / A
            a1 = -2 * np.cos(omega)
            a2 = 1 - alpha / A

            # Normalize by a0
            self.b = np.array([b0, b1, b2]) / a0
            self.a = np.array([1.0, a1, a2]) / a0

    def process_sound(self, sound):
        """
        Apply equalization to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be processed

        Returns:
            pygame.mixer.Sound: A new, equalized Sound object
        """
        try:
            # Design filter if not already done
            self._design_filter()

            # Convert sound to numpy array using sndarray (safer than raw bytes)
            samples = sndarray.array(sound)

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                # Mono audio
                processed = self._filter_channel(samples, 0)
            else:
                # Stereo audio - process each channel independently
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._filter_channel(samples[:, channel], channel)

            # Convert back to original data type and create new sound
            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Equalizer error: {e}")
            # Return original sound if processing fails
            return sound

    def _filter_channel(self, samples, channel_id):
        """
        Apply IIR filter to a single channel with proper state management.

        Args:
            samples: Input samples for one channel
            channel_id: Channel identifier for state tracking

        Returns:
            numpy.ndarray: Filtered samples
        """
        # Convert to float for processing
        x = samples.astype(np.float64)
        y = np.zeros_like(x)

        # Initialize or get filter history for this channel
        if channel_id not in self.x_history:
            self.x_history[channel_id] = [0.0, 0.0]  # x[n-1], x[n-2]
            self.y_history[channel_id] = [0.0, 0.0]  # y[n-1], y[n-2]

        x_hist = self.x_history[channel_id]
        y_hist = self.y_history[channel_id]

        # Apply IIR filter: y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
        for n in range(len(x)):
            # Current input
            x_n = x[n]

            # Calculate output
            y[n] = (self.b[0] * x_n +
                    self.b[1] * x_hist[0] +
                    self.b[2] * x_hist[1] -
                    self.a[1] * y_hist[0] -
                    self.a[2] * y_hist[1])

            # Update history
            x_hist[1] = x_hist[0]  # x[n-2] = x[n-1]
            x_hist[0] = x_n  # x[n-1] = x[n]

            y_hist[1] = y_hist[0]  # y[n-2] = y[n-1]
            y_hist[0] = y[n]  # y[n-1] = y[n]

        # Store updated history
        self.x_history[channel_id] = x_hist
        self.y_history[channel_id] = y_hist

        return y

    def reset_filter_state(self):
        """Reset filter memory (useful when switching between different sounds)."""
        self.x_history.clear()
        self.y_history.clear()


class SimpleEqualizer(AudioPlugin):
    """
    A simpler, faster equalizer using frequency domain processing.
    Good for basic tone shaping without the complexity of IIR filters.
    """

    def __init__(self, low_gain_db=0.0, mid_gain_db=0.0, high_gain_db=0.0):
        """
        Initialize simple 3-band equalizer.

        Args:
            low_gain_db (float): Low frequency gain (< 300Hz)
            mid_gain_db (float): Mid frequency gain (300Hz - 3kHz)
            high_gain_db (float): High frequency gain (> 3kHz)
        """
        self.low_gain = 10 ** (low_gain_db / 20.0)
        self.mid_gain = 10 ** (mid_gain_db / 20.0)
        self.high_gain = 10 ** (high_gain_db / 20.0)

    def process_sound(self, sound):
        """Apply simple 3-band EQ using frequency domain processing."""
        try:
            samples = sndarray.array(sound)
            sample_rate = pygame.mixer.get_init()[0]

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._eq_channel(samples, sample_rate)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._eq_channel(samples[:, channel], sample_rate)

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Simple EQ error: {e}")
            return sound

    def _eq_channel(self, samples, sample_rate):
        """Apply frequency domain EQ to one channel."""
        # Convert to float
        audio = samples.astype(np.float64)

        # FFT
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)

        # Apply gains to different frequency bands
        gains = np.ones_like(freqs)
        gains[freqs < 300] *= self.low_gain  # Low frequencies
        gains[(freqs >= 300) & (freqs < 3000)] *= self.mid_gain  # Mid frequencies
        gains[freqs >= 3000] *= self.high_gain  # High frequencies

        # Apply gains and convert back
        fft_processed = fft * gains
        processed = np.fft.irfft(fft_processed, len(audio))

        return processed
