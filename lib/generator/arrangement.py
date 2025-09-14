from lib.generator.bar import BarGenerator
from lib.generator.base import Generator
from lib.narrative.signature import make_signature_key


class ArrangementGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)

        self.bar_generator = BarGenerator(config)

    def generate(self, bars, key, *args):
        song_structure = [
            ('intro', 2),
            ("verse", 8),
            ("chorus", 8),
            ("verse", 8),
            ("chorus", 8),
            ("bridge", 8),
            ("chorus", 8),
            ("outro", 4)
        ]

        current_bar = 0
        full_song = []

        for section_name, num_bars in song_structure:
            for _ in range(num_bars):
                bar = self.bar_generator.generate(bar=current_bar, key=key)
                full_song.append(bar)
                current_bar += 1

        return full_song, make_signature_key(full_song)
