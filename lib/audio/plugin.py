class AudioPlugin:
    """Base class for all audio processing plugins."""

    def process_sound(self, sound):
        """
        Process a pygame Sound object.

        Args:
            sound (pygame.mixer.Sound): Input sound

        Returns:
            pygame.mixer.Sound: Processed sound
        """
        raise NotImplementedError("Subclasses must implement process_sound")
