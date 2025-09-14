from lib.narrative.bar import Bar
from lib.generator.base import Generator
from lib.generator.bar import BarGenerator
from lib.narrative.signature import make_signature_key


class NarrativeGenerator(Generator):
    """
    Generates a melody and rhythm based on a musical narrative,
    returning a structured list of bars.
    """

    def __init__(self, config=None):
        if config is None:
            config = {}
        super().__init__(config)
        self.bar_generator = BarGenerator(config=config)

    def generate(self, key, bars=8, *args):
        """
        Generates a list of Bar objects, each containing a chord and
        the melody notes with their specific rhythms for that bar.
        """
        # The final list of structured bar data
        narrative_data = []

        for bar in range(bars):
            bar_data: Bar = self.bar_generator.generate(bar + 1, key)
            if bar_data:
                narrative_data.append(bar_data)

        return narrative_data, make_signature_key(narrative_data)
