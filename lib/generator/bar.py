from lib.narrative.bar import Bar
from lib.generator.base import Generator
from lib.generator.chords import ChordsGenerator
from lib.generator.drums import DrumsGenerator
from lib.generator.melody import MelodyGenerator


class BarGenerator(Generator):

    def __init__(self, config=None):
        if config is None:
            config = {}

        super().__init__(config)

        self.melody_generator = MelodyGenerator(config)
        self.chords_generator = ChordsGenerator(config)
        self.bass_generator = None
        self.drums_generator = DrumsGenerator(config)

    def generate(self, bar, key, *args) -> Bar:
        chords = self.chords_generator.generate(bar=bar, key=key)
        # Get the current bar's chord to pass to the melody generator
        current_bar_chord = chords[0][0] if chords else None
        melody = self.melody_generator.generate(bar=bar, key=key, current_bar_chord=current_bar_chord)
        if 'enable_drums' in self.config and self.config['enable_drums']:
            kicks, hi_hats = self.drums_generator.generate(bar=bar, key=key)
            return Bar(chords=chords, melody_notes=melody, drums=(kicks, hi_hats))
        return Bar(chords=chords, melody_notes=melody)