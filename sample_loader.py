import pygame
import json

def load_samples(sample_path):
    """
    Loads sample from a dictionary of 'note_name': 'file_path'.
    In a real scenario, this would load the actual audio data into memory.
    """
    with open(sample_path, 'r') as samples_json:
        samples = json.load(samples_json)
    print("Loading sample...")
    for name, path in samples.items():
        samples[name] = pygame.mixer.Sound(path)
        print(f"Loaded: {name} from {path}")
    return samples
