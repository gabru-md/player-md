from lib.media.narrative.bar import Bar
from lib.media.narrative.generator import Generator
from lib.media.narrative.generator.chords import ChordsGenerator
from lib.media.narrative.generator.melody import MelodyGenerator


class BarGenerator(Generator):

    def __init__(self, config=None):
        if config is None:
            config = {}

        super().__init__(config)

        self.melody_generator = MelodyGenerator(config)
        self.chords_generator = ChordsGenerator(config)
        self.bass_generator = None
        self.drums_generator = None

    def generate(self, bar, key) -> Bar:
        chords = self.chords_generator.generate(bar=bar, key=key)
        melody = self.melody_generator.generate(bar=bar, key=key)

        return Bar(chords=chords, melody_notes=melody)
