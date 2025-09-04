import pygame
import json

from audio_compressor import AudioCompressor


def load_samples(sample_path, compressor: AudioCompressor = AudioCompressor(), note_compressor: AudioCompressor = AudioCompressor(gain=0.8)):
    """
    Loads sample from a dictionary of 'note_name': 'file_path'.
    In a real scenario, this would load the actual audio data into memory.
    """
    with open(sample_path, 'r') as samples_json:
        samples = json.load(samples_json)
    # print("Loading sample...")
    for name, path in samples.items():
        sound = pygame.mixer.Sound(path)
        if name.endswith("_note.wav"):
            sound = note_compressor.process_sound(sound)
        elif compressor:
            sound = compressor.process_sound(sound)

        samples[name] = sound
        # print(f"Loaded: {name} from {path}")
    return samples
