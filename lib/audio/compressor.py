import pygame
import pygame.sndarray as sndarray
import numpy as np

from lib.audio.plugin import AudioPlugin


class Compressor(AudioPlugin):
    """
    A robust audio compressor that processes Pygame Sound objects.

    This class applies a compression algorithm to audio data using safe
    sndarray operations to avoid byte conversion errors. Works with both
    mono and stereo audio.
    """

    def __init__(self, threshold_db=-20.0, ratio=4.0, attack_ms=10, release_ms=100, makeup_gain_db=0.0):
        """
        Initialize the compressor with key parameters.

        Args:
            threshold_db (float): The threshold in decibels
            ratio (float): The compression ratio (e.g., 4.0 = 4:1)
            attack_ms (float): The attack time in milliseconds
            release_ms (float): The release time in milliseconds
            makeup_gain_db (float): Makeup gain in dB to compensate for level reduction
        """
        self.threshold = 10 ** (threshold_db / 20.0)  # Convert dB to linear amplitude
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.makeup_gain = 10 ** (makeup_gain_db / 20.0)

        # Envelope follower state for each channel
        self.envelope_state = {}

    def process_sound(self, sound):
        """
        Apply compression to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be compressed

        Returns:
            pygame.mixer.Sound: A new, compressed Sound object
        """
        try:
            # Convert sound to numpy array using sndarray (safer than raw bytes)
            samples = sndarray.array(sound)

            # Get sample rate
            sample_rate = pygame.mixer.get_init()[0]
            if sample_rate is None:
                raise RuntimeError("Pygame mixer not initialized")

            # Calculate time constants
            attack_coeff = np.exp(-1.0 / (sample_rate * self.attack_ms / 1000.0))
            release_coeff = np.exp(-1.0 / (sample_rate * self.release_ms / 1000.0))

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                # Mono audio
                processed = self._compress_channel(samples, 0, attack_coeff, release_coeff)
            else:
                # Stereo audio - process each channel
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._compress_channel(
                        samples[:, channel], channel, attack_coeff, release_coeff
                    )

            # Apply makeup gain
            processed *= self.makeup_gain

            # Convert back to original data type and create new sound
            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Compressor error: {e}")
            # Return original sound if processing fails
            return sound

    def _compress_channel(self, samples, channel_id, attack_coeff, release_coeff):
        """
        Apply compression to a single channel.

        Args:
            samples: Input samples for one channel
            channel_id: Channel identifier for state tracking
            attack_coeff: Pre-calculated attack coefficient
            release_coeff: Pre-calculated release coefficient

        Returns:
            numpy.ndarray: Compressed samples
        """
        # Convert to float for processing
        audio = samples.astype(np.float64)

        # Initialize envelope state for this channel
        if channel_id not in self.envelope_state:
            self.envelope_state[channel_id] = 0.0

        envelope = self.envelope_state[channel_id]
        output = np.zeros_like(audio)

        # Process each sample
        for i in range(len(audio)):
            # Get current sample amplitude
            sample_amplitude = abs(audio[i]) / 32768.0  # Normalize to 0-1

            # Envelope follower (peak detector)
            if sample_amplitude > envelope:
                # Attack: follow peaks quickly
                envelope = sample_amplitude + (envelope - sample_amplitude) * attack_coeff
            else:
                # Release: decay slowly
                envelope = sample_amplitude + (envelope - sample_amplitude) * release_coeff

            # Calculate gain reduction
            if envelope > self.threshold:
                # Calculate compression
                over_threshold = envelope - self.threshold
                compressed_over = over_threshold / self.ratio
                target_level = self.threshold + compressed_over
                gain_reduction = target_level / envelope if envelope > 0 else 1.0
            else:
                # No compression needed
                gain_reduction = 1.0

            # Apply compression
            output[i] = audio[i] * gain_reduction

        # Store envelope state for next call
        self.envelope_state[channel_id] = envelope

        return output

    def reset_state(self):
        """Reset compressor state (useful when switching between different sounds)."""
        self.envelope_state.clear()


class SimpleCompressor(AudioPlugin):
    """
    A simpler, faster compressor using vectorized operations.
    Good for basic dynamic range control without sample-by-sample processing.
    """

    def __init__(self, threshold_db=-20.0, ratio=4.0, makeup_gain_db=0.0):
        """
        Initialize simple compressor.

        Args:
            threshold_db (float): Compression threshold in dB
            ratio (float): Compression ratio
            makeup_gain_db (float): Makeup gain in dB
        """
        self.threshold = 10 ** (threshold_db / 20.0)
        self.ratio = ratio
        self.makeup_gain = 10 ** (makeup_gain_db / 20.0)

    def process_sound(self, sound):
        """Apply simple compression using vectorized operations."""
        try:
            samples = sndarray.array(sound)

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._simple_compress(samples)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._simple_compress(samples[:, channel])

            # Apply makeup gain
            processed *= self.makeup_gain

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Simple compressor error: {e}")
            return sound

    def _simple_compress(self, samples):
        """Apply vectorized compression to one channel."""
        audio = samples.astype(np.float64)

        # Calculate amplitudes
        amplitudes = np.abs(audio) / 32768.0

        # Vectorized compression calculation
        over_threshold = np.maximum(0, amplitudes - self.threshold)
        compressed_over = over_threshold / self.ratio
        target_levels = self.threshold + compressed_over

        # Calculate gain reduction ratios
        gain_reductions = np.where(amplitudes > 0,
                                   target_levels / amplitudes,
                                   1.0)

        # Ensure no amplification above threshold
        gain_reductions = np.minimum(gain_reductions, 1.0)

        # Apply compression
        output = audio * gain_reductions

        return output


class MultibandCompressor(AudioPlugin):
    """
    A multiband compressor that splits the signal into frequency bands
    and applies different compression settings to each band.
    """

    def __init__(self,
                 low_threshold_db=-25.0, low_ratio=3.0,
                 mid_threshold_db=-20.0, mid_ratio=4.0,
                 high_threshold_db=-15.0, high_ratio=6.0,
                 makeup_gain_db=3.0):
        """
        Initialize multiband compressor.

        Args:
            low_threshold_db: Low band threshold (< 300Hz)
            low_ratio: Low band compression ratio
            mid_threshold_db: Mid band threshold (300Hz - 3kHz)
            mid_ratio: Mid band compression ratio
            high_threshold_db: High band threshold (> 3kHz)
            high_ratio: High band compression ratio
            makeup_gain_db: Overall makeup gain
        """
        self.low_comp = SimpleCompressor(low_threshold_db, low_ratio, 0)
        self.mid_comp = SimpleCompressor(mid_threshold_db, mid_ratio, 0)
        self.high_comp = SimpleCompressor(high_threshold_db, high_ratio, 0)
        self.makeup_gain = 10 ** (makeup_gain_db / 20.0)

    def process_sound(self, sound):
        """Apply multiband compression."""
        try:
            samples = sndarray.array(sound)
            sample_rate = pygame.mixer.get_init()[0]

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._multiband_compress(samples, sample_rate)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._multiband_compress(samples[:, channel], sample_rate)

            # Apply makeup gain
            processed *= self.makeup_gain

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Multiband compressor error: {e}")
            return sound

    def _multiband_compress(self, samples, sample_rate):
        """Apply multiband compression to one channel using FFT."""
        audio = samples.astype(np.float64)

        # FFT
        fft = np.fft.rfft(audio)
        freqs = np.fft.rfftfreq(len(audio), 1 / sample_rate)

        # Split into bands
        low_mask = freqs < 300
        mid_mask = (freqs >= 300) & (freqs < 3000)
        high_mask = freqs >= 3000

        # Process each band separately by converting back to time domain
        low_fft = fft.copy()
        low_fft[~low_mask] = 0
        low_audio = np.fft.irfft(low_fft, len(audio))

        mid_fft = fft.copy()
        mid_fft[~mid_mask] = 0
        mid_audio = np.fft.irfft(mid_fft, len(audio))

        high_fft = fft.copy()
        high_fft[~high_mask] = 0
        high_audio = np.fft.irfft(high_fft, len(audio))

        # Compress each band
        low_compressed = self.low_comp._simple_compress(low_audio.astype(np.int16))
        mid_compressed = self.mid_comp._simple_compress(mid_audio.astype(np.int16))
        high_compressed = self.high_comp._simple_compress(high_audio.astype(np.int16))

        # Sum the bands back together
        return low_compressed + mid_compressed + high_compressed
