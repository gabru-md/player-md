import random

from lib.generator.base import Generator


class DrumsGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)

        # Common drum patterns for kicks and hi-hats
        self.kick_patterns = [
            [0],  # Kick on the downbeat
            [0, 2],  # Kick on beats 1 and 3
            [0, 1.5, 3],  # Kick on 1, "and" of 2, and 4
            [0, 3],  # Kick on beats 1 and 4
        ]

        self.hihat_patterns = [
            [0, 1, 2, 3],  # Hi-hat on every beat
            [0.5, 1.5, 2.5, 3.5],  # Hi-hat on every off-beat ("and")
            [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],  # Hi-hat on every eighth note
            [0.5, 1, 1.5, 2.5, 3, 3.5],  # Dotted hi-hat pattern
        ]

    def generate(self, bar, key=None, *args):

        kick_rhythm = random.choice(self.kick_patterns)
        hihat_rhythm = random.choice(self.hihat_patterns)

        kick_notes = [('Kick', offset) for offset in kick_rhythm]
        hihat_notes = [('HiHat', offset) for offset in hihat_rhythm]

        return kick_notes, hihat_notes
