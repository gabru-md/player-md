import random
from lib.bar import Bar
from lib.signature import make_signature_key


class NarrativeGenerator:
    """
    Generates a melody and rhythm based on a musical narrative,
    returning a structured list of bars.
    """

    def __init__(self):
        self.rhythm_patterns = [
            [],
            # Quarter notes
            [0.5, 1.5, 3.5],
            # Half notes
            [0, 2],
            # Dotted quarter and eighth note
            [0, 1.5],
        ]

        # Rhythm for the "silence" sections (very sparse)
        self.silence_rhythm_patterns = [
            [],
            # Single note at the end of the bar
            [3.5],
            # Two notes spaced far apart
            [0, 3],
            # Extra silence
            []
        ]

        # Rhythm for the "buildup" and "tension" sections (fast, dense)
        self.buildup_rhythm_patterns = [
            [],
            # Eighth notes
            # [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],
            # Dotted rhythms
            # [0.75, 1.5, 2.25, 3.75],

            # [0.25, 1.25, 2.25, 3.25]
        ]

        self.release_rhythm_patterns = [
            [0, 2],
            [0]
        ]

        # Chord progression patterns based on scale degrees (e.g., 0=root, 3=fourth)
        self.chord_patterns = {
            "standard": [0, 4, 5, 3],  # I-V-vi-IV (e.g., C-G-Am-F)
            "jazz_blues": [0, 3, 4, 0],  # I-IV-V-I (e.g., C-F-G-C)
            "pop_hit": [0, 5, 3, 4],  # I-vi-IV-V (e.g., C-Am-F-G)
            "dramatic": [0, 5, 3, 4],  # I-vi-IV-V (e.g., C-Am-F-G)
        }

        # Rhythm for the chords.
        self.simple_chord_rhythm_patterns = [
            [0, 2],
            [0, 3]
        ]
        self.release_chord_rhythm_patterns = [
            [0],
            [0, 2]
        ]
        self.buildup_chord_rhythm_patterns = [
            [0, 1, 2, 3],
            # [0, 1, 1.5, 2, 2.5, 3]
        ]

    def generate_narrative(self, key, bars=8):
        """
        Generates a list of Bar objects, each containing a chord and
        the melody notes with their specific rhythms for that bar.
        """
        # The final list of structured bar data
        narrative_data = []

        chords_in_key = key.chords
        notes_in_key = key.notes

        # Select a random chord pattern and build the full progression
        pattern_name, selected_pattern = random.choice(list(self.chord_patterns.items()))
        chord_progression = []
        for i in range(bars):
            # The modulo operator (%) ensures the pattern repeats if bars > len(selected_pattern)
            chord_degree = selected_pattern[i % len(selected_pattern)]

            # Use min() to ensure the degree does not exceed the available chords in the key
            safe_chord_degree = min(chord_degree, len(chords_in_key) - 1)
            chord_progression.append(chords_in_key[safe_chord_degree])

        # --- Section 1: Conversation (Bars 1-2) ---
        for bar in range(2):
            # Select a random rhythm pattern for each bar
            melody_rhythm = random.choice(self.rhythm_patterns)
            melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
            simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
            chords = [(chord_progression[bar], offset) for offset in simple_chord_rhythm]
            narrative_data.append(Bar(chords, melody_notes))

        # --- Section 2: Silence (Bar 3) ---
        melody_rhythm = random.choice(self.silence_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[2], offset) for offset in simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 3: Conversation (Bar 4) ---
        melody_rhythm = random.choice(self.rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[3], offset) for offset in simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 4: Silence (Bar 5) ---
        melody_rhythm = random.choice(self.silence_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[4], offset) for offset in simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 5: Buildup & Tension (Bars 6-7) ---
        for bar in range(2):
            melody_rhythm = random.choice(self.buildup_rhythm_patterns)
            melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
            buildup_chord_rhythm = random.choice(self.buildup_chord_rhythm_patterns)
            chords = [(chord_progression[5 + bar], offset) for offset in buildup_chord_rhythm]
            narrative_data.append(Bar(chords, melody_notes))

        # --- Section 6: Release (Bar 8) ---
        melody_rhythm = random.choice(self.release_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        release_chord_rhythm = random.choice(self.release_chord_rhythm_patterns)
        chords = [(chord_progression[7], offset) for offset in release_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        return narrative_data, make_signature_key(narrative_data)
