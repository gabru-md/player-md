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

        repeaters = {}

        for section_name, num_bars in song_structure:
            repeater_key = f"{section_name}_{num_bars}"
            if key in repeaters:
                full_song.extend(repeaters[repeater_key])

            else:
                bars = []
                for _ in range(num_bars):
                    bar = self.bar_generator.generate(bar=current_bar, key=key)
                    bars.append(bar)
                    current_bar += 1
                repeaters[repeater_key] = bars
                full_song.extend(bars)

        return full_song, make_signature_key(full_song)
