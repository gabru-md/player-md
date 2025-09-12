import random

from lib.media.narrative.generator import Generator


class ChordsGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)
        self.chords_pattern = [0, 4, 5, 3]  # I-V-vi-IV (e.g., C-G-Am-F)
        self.chords_rhythms = [
            [0],
            [0, 2],
            [1, 2],
            [0, 3],
            [0, 1, 2, 3]
        ]

    def generate(self, bar, key):
        chords_in_key = key.chords

        chord_degree = self.chords_pattern[bar % len(self.chords_pattern)]
        safe_chord_degree = min(chord_degree, len(chords_in_key) - 1)

        chord = chords_in_key[safe_chord_degree]
        chords_rhythm = random.choice(self.chords_rhythms)

        return [(chord, offset) for offset in chords_rhythm]
