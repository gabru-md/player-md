import random

from lib.media.narrative.generator import Generator


class MelodyGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)
        self.no_melody_in_bars = [1]  # bars to exclude any melody notes from
        self.melody_rhythms = [
            [0.5, 1.5, 3.5],
            [0, 1.5],
            [3.5],
            [0, 3],
            [],
            [0.5, 1.5, 2.5, 3.5],
            # [0.25, 0.5, 0.75, 1.0, 2.25, 2.5, 2.75, 3.0]
        ]

    def generate(self, bar, key):
        melody_rhythm = random.choice(self.melody_rhythms)
        return [(random.choice(key.notes), offset) for offset in melody_rhythm]
