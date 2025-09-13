import random

from lib.narrative.generator.base import Generator


class ChordsGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)
        # Using a Markov chain to define chord transitions
        self.chord_transitions = {
            0: [0, 1, 3, 4, 5],  # I can go to I, ii, IV, V, vi
            1: [4],  # ii often goes to V
            3: [1, 4],  # IV can go to ii or V
            4: [0, 5],  # V strongly resolves to I or vi
            5: [3, 1],  # vi often goes to IV or ii
        }
        self.previous_chord_degree = 0  # Start with the tonic (I)

    def generate(self, bar, key, *args):
        chords_in_key = key.chords

        # Get possible next chords based on the previous chord
        possible_next_degrees = self.chord_transitions.get(self.previous_chord_degree)

        # If the previous chord has no defined transitions, default to the I chord
        if not possible_next_degrees:
            possible_next_degrees = [0]

        # Select a chord degree from the possible transitions
        chord_degree = random.choice(possible_next_degrees)
        self.previous_chord_degree = chord_degree  # Update the state for the next bar

        safe_chord_degree = min(chord_degree, len(chords_in_key) - 1)
        chord = chords_in_key[safe_chord_degree]

        # Keeping the existing rhythm logic
        chords_rhythms = [
            [0],
            [0, 2],
            [1, 2],
            [0, 3],
            [0, 1, 2, 3]
        ]
        chords_rhythm = random.choice(chords_rhythms)

        chords = [(chord, offset) for offset in chords_rhythm]
        return chords