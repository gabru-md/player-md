import pygame
import pygame.sndarray as sndarray
import numpy as np


class Limiter:
    """
    A robust audio limiter that processes Pygame Sound objects.

    This limiter prevents audio from exceeding a specified threshold,
    with smooth attack and release characteristics to avoid distortion.
    Works with both mono and stereo audio.
    """

    def __init__(self, threshold_db=-3.0, attack_ms=1, release_ms=50, lookahead_ms=5):
        """
        Initialize the limiter.

        Args:
            threshold_db (float): Maximum output level in decibels (typically -3 to -1 dB)
            attack_ms (float): Attack time in milliseconds (very fast for limiting)
            release_ms (float): Release time in milliseconds
            lookahead_ms (float): Lookahead time to prevent overshoot
        """
        self.threshold = 10 ** (threshold_db / 20.0)  # Convert dB to linear
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self.lookahead_ms = lookahead_ms

        # Internal state for smooth gain reduction
        self.envelope = 1.0

    def process_sound(self, sound):
        """
        Apply limiting to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be limited

        Returns:
            pygame.mixer.Sound: A new, limited Sound object
        """
        try:
            # Convert sound to numpy array using sndarray (safer than raw bytes)
            samples = sndarray.array(sound)

            # Get mixer settings
            sample_rate = pygame.mixer.get_init()[0]
            if sample_rate is None:
                raise RuntimeError("Pygame mixer not initialized")

            # Calculate time constants in samples
            attack_samples = max(1, int(sample_rate * (self.attack_ms / 1000.0)))
            release_samples = max(1, int(sample_rate * (self.release_ms / 1000.0)))
            lookahead_samples = int(sample_rate * (self.lookahead_ms / 1000.0))

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                # Mono audio
                processed = self._limit_channel(samples, attack_samples, release_samples, lookahead_samples)
            else:
                # Stereo audio - process each channel
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._limit_channel(
                        samples[:, channel], attack_samples, release_samples, lookahead_samples
                    )

            # Convert back to original data type and create new sound
            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Limiter error: {e}")
            # Return original sound if processing fails
            return sound

    def _limit_channel(self, samples, attack_samples, release_samples, lookahead_samples):
        """
        Apply limiting to a single channel.

        Args:
            samples: Input samples for one channel
            attack_samples: Attack time in samples
            release_samples: Release time in samples
            lookahead_samples: Lookahead time in samples

        Returns:
            numpy.ndarray: Processed samples
        """
        # Convert to float for processing
        audio = samples.astype(np.float64)
        length = len(audio)

        # Create output buffer
        output = np.zeros_like(audio)

        # Initialize envelope follower
        envelope = self.envelope

        # Process with lookahead
        for i in range(length):
            # Look ahead to find peak in upcoming samples
            lookahead_end = min(i + lookahead_samples, length)
            peak_amplitude = 0.0

            for j in range(i, lookahead_end):
                amplitude = abs(audio[j]) / 32768.0  # Normalize to 0-1 range
                peak_amplitude = max(peak_amplitude, amplitude)

            # Calculate required gain reduction
            if peak_amplitude > self.threshold:
                target_gain = self.threshold / peak_amplitude
            else:
                target_gain = 1.0

            # Smooth gain changes
            if target_gain < envelope:
                # Attack phase (gain reduction)
                envelope = target_gain + (envelope - target_gain) * np.exp(-1.0 / attack_samples)
            else:
                # Release phase (gain recovery)
                envelope = target_gain + (envelope - target_gain) * np.exp(-1.0 / release_samples)

            # Apply gain reduction
            output[i] = audio[i] * envelope

        # Store envelope state for next call
        self.envelope = envelope

        return output


class FastLimiter:
    """
    Ultra-fast limiter using pure numpy operations.
    Sacrifices some audio quality for maximum speed.
    """

    def __init__(self, threshold_db=-3.0, release_factor=0.995):
        """
        Initialize fast limiter.

        Args:
            threshold_db (float): Maximum output level in decibels
            release_factor (float): Release smoothing (0.99-0.999)
        """
        self.threshold = 10 ** (threshold_db / 20.0)
        self.release_factor = release_factor
        self.gain = 1.0

    def process_sound(self, sound):
        """Apply ultra-fast limiting using vectorized operations."""
        try:
            samples = sndarray.array(sound)

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._fast_limit(samples)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._fast_limit(samples[:, channel])

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Fast limiter error: {e}")
            return sound

    def _fast_limit(self, samples):
        """Apply vectorized limiting - MUCH faster but less precise."""
        audio = samples.astype(np.float64)

        # Vectorized amplitude calculation
        amplitudes = np.abs(audio) / 32768.0

        # Simple hard limiting (no smooth envelope)
        gains = np.where(amplitudes > self.threshold,
                         self.threshold / amplitudes,
                         1.0)

        # Apply limiting
        output = audio * gains

        return output


class SimpleLimiter:
    """
    A simpler, more CPU-efficient limiter with basic peak detection.
    Good balance between speed and quality.
    """

    def __init__(self, threshold_db=-3.0, release_factor=0.999):
        """
        Initialize simple limiter.

        Args:
            threshold_db (float): Maximum output level in decibels
            release_factor (float): Release smoothing (0.99-0.999, higher = slower release)
        """
        self.threshold = 10 ** (threshold_db / 20.0)
        self.release_factor = release_factor
        self.gain = 1.0

    def process_sound(self, sound):
        """Apply simple limiting to a Pygame Sound object."""
        try:
            samples = sndarray.array(sound)

            # Handle both mono and stereo
            if len(samples.shape) == 1:
                processed = self._simple_limit(samples)
            else:
                processed = np.zeros_like(samples, dtype=np.float64)
                for channel in range(samples.shape[1]):
                    processed[:, channel] = self._simple_limit(samples[:, channel])

            processed = np.clip(processed, -32768, 32767).astype(samples.dtype)
            return sndarray.make_sound(processed)

        except Exception as e:
            print(f"Simple limiter error: {e}")
            return sound

    def _simple_limit(self, samples):
        """Apply simple limiting to one channel."""
        audio = samples.astype(np.float64)
        amplitudes = np.abs(audio) / 32768.0

        # Vectorized gain calculation with envelope following
        gains = np.ones(len(audio))
        current_gain = self.gain

        for i in range(len(audio)):
            amplitude = amplitudes[i]

            if amplitude > self.threshold:
                required_gain = self.threshold / amplitude
                current_gain = min(current_gain, required_gain)
            else:
                current_gain = current_gain * self.release_factor + (1.0 - self.release_factor)
                current_gain = min(current_gain, 1.0)

            gains[i] = current_gain

        self.gain = current_gain
        return audio * gains