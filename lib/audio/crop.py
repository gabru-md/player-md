import pygame
from pygame import sndarray

from lib.audio.plugin import AudioPlugin


class CropPlugin(AudioPlugin):
    """
    Plugin to crop audio to a specific portion.
    """

    def __init__(self, start_ratio=0.0, end_ratio=0.5, fade_ms=10):
        """
        Initialize crop plugin.

        Args:
            start_ratio (float): Start position as ratio of total length (0.0 = beginning)
            end_ratio (float): End position as ratio of total length (0.5 = halfway, 1.0 = end)
            fade_ms (float): Fade in/out duration in milliseconds to avoid clicks
        """
        self.start_ratio = max(0.0, min(1.0, start_ratio))
        self.end_ratio = max(0.0, min(1.0, end_ratio))
        self.fade_ms = fade_ms

        if self.start_ratio >= self.end_ratio:
            raise ValueError("start_ratio must be less than end_ratio")

    def process_sound(self, sound):
        """Crop the sound to specified portion."""
        try:
            samples = sndarray.array(sound)
            sample_rate = pygame.mixer.get_init()[0]

            # Calculate crop points
            total_samples = len(samples) if len(samples.shape) == 1 else len(samples[:, 0])
            start_sample = int(total_samples * self.start_ratio)
            end_sample = int(total_samples * self.end_ratio)

            # Calculate fade samples
            fade_samples = int(sample_rate * self.fade_ms / 1000.0)
            fade_samples = min(fade_samples, (end_sample - start_sample) // 4)  # Max 25% of crop length

            # Crop the audio
            if len(samples.shape) == 1:
                # Mono
                cropped = samples[start_sample:end_sample].copy()
            else:
                # Stereo
                cropped = samples[start_sample:end_sample, :].copy()

            # Apply fade in/out to avoid clicks
            if fade_samples > 0:
                cropped = self._apply_fades(cropped, fade_samples)

            return sndarray.make_sound(cropped)

        except Exception as e:
            print(f"Crop plugin error: {e}")
            return sound

    def _apply_fades(self, samples, fade_samples):
        """Apply fade in and fade out to avoid clicks."""
        if len(samples.shape) == 1:
            # Mono
            # Fade in
            for i in range(fade_samples):
                fade_gain = i / fade_samples
                samples[i] = samples[i] * fade_gain

            # Fade out
            for i in range(fade_samples):
                fade_gain = (fade_samples - i) / fade_samples
                samples[-(i + 1)] = samples[-(i + 1)] * fade_gain
        else:
            # Stereo
            # Fade in
            for i in range(fade_samples):
                fade_gain = i / fade_samples
                samples[i, :] = samples[i, :] * fade_gain

            # Fade out
            for i in range(fade_samples):
                fade_gain = (fade_samples - i) / fade_samples
                samples[-(i + 1), :] = samples[-(i + 1), :] * fade_gain

        return samples