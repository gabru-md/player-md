import pygame
import numpy as np

class Compressor:
    """
    A simple audio compressor that processes Pygame Sound objects.

    This class applies a basic compression algorithm to audio data. It's not a
    real-time processor and should be used to pre-process samples before playback.
    """

    def __init__(self, threshold_db=-20.0, ratio=4.0, attack_ms=10, release_ms=100, gain=1.0):
        """
        Initializes the compressor with key parameters.

        Args:
            threshold_db (float): The threshold in decibels.
            ratio (float): The compression ratio.
            attack_ms (int): The attack time in milliseconds.
            release_ms (int): The release time in milliseconds.
        """
        self.threshold = 10 ** (threshold_db / 20.0)  # Convert dB to linear amplitude
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
        self._gain = gain

    def process_sound(self, sound):
        """
        Applies compression to a Pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): The sound to be compressed.

        Returns:
            pygame.mixer.Sound: A new, compressed Sound object.
        """
        raw_data = sound.get_raw()
        samples = np.frombuffer(raw_data, dtype=np.int16)

        gain = self._gain

        # Calculate samples per millisecond for attack and release
        sample_rate = pygame.mixer.get_init()[0]
        attack_samples = int(sample_rate * (self.attack_ms / 1000.0))
        release_samples = int(sample_rate * (self.release_ms / 1000.0))

        processed_samples = np.copy(samples).astype(np.float32)

        # Simple gain reduction based on a peak envelope follower
        for i in range(len(processed_samples)):
            sample = processed_samples[i]
            amplitude = abs(sample) / 32768.0  # Normalize to -1 to 1

            if amplitude > self.threshold:
                # Compression is active
                gain_reduction = (amplitude - self.threshold) / self.ratio
                new_gain = self.threshold + gain_reduction
                gain = gain - (gain - new_gain) / (1 + attack_samples)
            else:
                # Release phase
                gain = gain + (1.0 - gain) / (1 + release_samples)

            processed_samples[i] = processed_samples[i] * gain

        processed_samples = np.clip(processed_samples, -32768, 32767).astype(np.int16)
        return pygame.mixer.Sound(processed_samples.tobytes())
