import random

from lib.narrative.generator.base import Generator
from lib.keys import Keys


class MelodyGenerator(Generator):

    def __init__(self, config):
        super().__init__(config)
        self.no_melody_in_bars = [1]  # bars to exclude any melody notes from
        self.previous_note = None
        # Weighted note durations for rhythm generation
        self.note_durations = {
            1.0: 6,  # Quarter note
            0.5: 8,  # Eighth note
            2.0: 4,  # Half note
            0.25: 3,  # Sixteenth note
            1.5: 2,  # Dotted quarter note
        }
        self.note_duration_keys = list(self.note_durations.keys())

    def generate_organic_rhythm(self, bar_length=4):
        rhythm_offsets = []
        current_beat = 0.0
        while current_beat < bar_length:

            remaining_beats = bar_length - current_beat

            # Filter durations that are too long for the rest of the bar
            valid_durations = [d for d in self.note_duration_keys if d <= remaining_beats]

            if not valid_durations:
                break

            # Weighted selection of the next duration
            weights = [self.note_durations[d] for d in valid_durations]
            next_duration = random.choices(valid_durations, weights=weights, k=1)[0]

            rhythm_offsets.append(current_beat)
            current_beat += next_duration

        return rhythm_offsets

    def generate(self, bar, key, current_bar_chord=None, *args):
        if bar in self.no_melody_in_bars:
            return []

        melody_rhythm = self.generate_organic_rhythm()
        melody_notes = []
        for offset in melody_rhythm:

            # Prioritize notes in the current chord and smooth motion
            possible_notes = []

            # HIGH WEIGHT FOR CHORD TONES
            current_chord_notes = []
            if current_bar_chord:
                current_chord_notes = Keys.get_notes_from_chord(current_bar_chord)
            possible_notes.extend([note for note in current_chord_notes for _ in range(5)])

            # MEDIUM WEIGHT FOR STEPWISE MOTION
            if self.previous_note and self.previous_note in key.notes:
                for note in key.notes:
                    if abs(key.notes.index(note) - key.notes.index(self.previous_note)) <= 2:
                        possible_notes.extend([note for _ in range(3)])

            # LOW WEIGHT FOR ANY OTHER NOTE IN THE KEY
            possible_notes.extend(key.notes)

            # Use random.choices for weighted selection
            next_note = random.choice(possible_notes)

            melody_notes.append((next_note, offset))
            self.previous_note = next_note

        return melody_notes