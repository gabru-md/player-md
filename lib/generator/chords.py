import random

from lib.generator.base import Generator


class ChordsGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)
        # Using a Markov chain with weighted transitions to make it more 'human'
        # The value is a tuple of (possible_next_degree, weight)
        self.chord_transitions = {
            # V is most likely to resolve to I.
            # IV can go to V or ii.
            # vi can go to IV or ii.
            0: [(0, 1), (1, 3), (3, 4), (4, 4), (5, 2)],  # I -> I, ii, IV, V, vi
            1: [(4, 5)],  # ii -> V (strong pull)
            3: [(1, 2), (4, 3)],  # IV -> ii, V
            4: [(0, 8), (5, 2)],  # V -> I (very strong resolution), or vi
            5: [(3, 4), (1, 2)],  # vi -> IV, ii
        }
        self.common_progressions = [
            [0, 5, 3, 4],  # I-vi-IV-V (a very common pop progression)
            [0, 3, 4, 0],  # I-IV-V-I (the classic blues/rock progression)
            [0, 1, 4, 0]  # I-ii-V-I (jazz standard progression)
        ]
        self.previous_chord_degree = 0  # Start with the tonic (I)
        self.progression_counter = 0

        # More varied and common chord rhythms
        self.chords_rhythms = [
            [0.0],  # Whole note
            [0.0, 2.0],  # Half notes
            [0.0, 1.0, 2.0, 3.0],  # Quarter notes
            [0.0, 1.5],  # Dotted quarter, dotted quarter (incomplete but sets a feel)
            [0.0, 0.5, 1.0, 1.5, 2.0],  # eighth notes
            [0.0, 0.5, 1.0, 2.0, 3.0],  # eighth notes and quarter notes
            [0.0, 0.5, 1.0, 2.5],  # A more syncopated rhythm
            [0.0, 1.0, 2.5],  # Another syncopated rhythm
        ]

    def generate_chord_rhythm(self):
        """Selects a more 'human' chord rhythm from pre-defined patterns."""
        return random.choice(self.chords_rhythms)

    def generate(self, bar, key, *args):
        chords_in_key = key.chords

        # Use a common progression every 4 bars for more structure
        if bar % 4 == 0 and bar > 0:
            progression_to_use = random.choice(self.common_progressions)
            self.progression_counter = 0
            chord_degree = progression_to_use[self.progression_counter]
            self.progression_counter += 1
        elif 0 < self.progression_counter < len(self.common_progressions[0]):
            # Continue the common progression
            progression_to_use = random.choice(self.common_progressions)
            chord_degree = progression_to_use[self.progression_counter]
            self.progression_counter += 1
        else:
            # Use the weighted Markov chain
            possible_next_transitions = self.chord_transitions.get(self.previous_chord_degree)

            if not possible_next_transitions:
                possible_next_transitions = [(0, 1)]  # Default to the tonic

            # Separate degrees and weights
            degrees, weights = zip(*possible_next_transitions)
            chord_degree = random.choices(degrees, weights=weights, k=1)[0]
            self.progression_counter = 0

        self.previous_chord_degree = chord_degree  # Update the state for the next bar

        safe_chord_degree = min(chord_degree, len(chords_in_key) - 1)
        chord = chords_in_key[safe_chord_degree]

        # Use the new rhythm generation method
        chords_rhythm = self.generate_chord_rhythm()

        chords = [(chord, offset) for offset in chords_rhythm]
        return chords