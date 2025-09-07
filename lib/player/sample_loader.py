import pygame
import json

from lib.audio.compressor import Compressor
from lib.audio.equalizer import Equalizer


def load_samples(sample_path, compressor: Compressor = Compressor(), note_compressor: Compressor = Compressor(gain=0.8),
                 slide_note_compressor=Compressor(gain=0.6, attack_ms=50),
                 chord_eq=Equalizer(center_frequency=170, gain_db=12), drums_compressor=Compressor(gain=0.8)):
    """
    Loads sample from a dictionary of 'note_name': 'file_path'.
    In a real scenario, this would load the actual audio data into memory.
    """
    with open(sample_path, 'r') as samples_json:
        samples = json.load(samples_json)
    # print("Loading sample...")
    for name, path in samples.items():
        sound = pygame.mixer.Sound(path)
        if name.endswith("_note"):
            if name.endswith("_slide_note"):
                sound = slide_note_compressor.process_sound(sound)
            else:
                sound = note_compressor.process_sound(sound)
        elif name.endswith("_chord"):  # chords
            if chord_eq:
                sound = chord_eq.process_sound(sound)
            sound = compressor.process_sound(sound)
        else:
            sound = drums_compressor.process_sound(sound)

        samples[name] = sound
        # print(f"Loaded: {name} from {path}")
    return samples
