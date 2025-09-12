import pygame
import json

from lib.audio.compressor import Compressor, MultibandCompressor
from lib.audio.crop import CropPlugin
from lib.audio.equalizer import Equalizer
from lib.audio.filter import FilterPresets
from lib.audio.limiter import FastLimiter
from lib.log import Logger

SAMPLES = None

log = Logger.get_log("SampleLoader")


def load_samples(sample_path,
                 compressor: Compressor = Compressor(),
                 note_compressor: Compressor = Compressor(makeup_gain_db=0.8),
                 slide_note_compressor=Compressor(makeup_gain_db=0.6, attack_ms=50),
                 chord_eq=Equalizer(center_frequency=187, gain_db=15),
                 chords_limiter=FastLimiter(threshold_db=-25),
                 bass_eq=Equalizer(center_frequency=170, gain_db=-15),
                 bass_compressor=MultibandCompressor(high_threshold_db=-40, mid_threshold_db=-40, low_threshold_db=-40,
                                                     low_ratio=1.0, mid_ratio=2.0),
                 drums_compressor=Compressor(makeup_gain_db=0.8),
                 bass_limiter=FastLimiter(threshold_db=-45.0),
                 bass_crop=CropPlugin(),
                 bass_filter=FilterPresets.treble_cut(),
                 force_reload=False):
    """
    Loads sample from a dictionary of 'note_name': 'file_path'.
    In a real scenario, this would load the actual audio data into memory.
    """

    global SAMPLES

    if not force_reload:
        if SAMPLES:
            return SAMPLES

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
                sound = chords_limiter.process_sound(sound)
            sound = compressor.process_sound(sound)
        elif name.endswith('_bass'):
            sound = bass_eq.process_sound(sound)
            sound = bass_filter.process_sound(sound)
            sound = bass_compressor.process_sound(sound)
            sound = bass_limiter.process_sound(sound)
        else:
            sound = drums_compressor.process_sound(sound)

        samples[name] = sound
    SAMPLES = samples
    log.info("Loading Samples finished")
    return samples
