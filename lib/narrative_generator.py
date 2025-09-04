import random
from bar import Bar
from signature import make_signature_key

class NarrativeGenerator:
    """
    Generates a melody and rhythm based on a musical narrative,
    returning a structured list of bars.
    """

    def __init__(self):
        # Rhythm for the "conversation" sections (simple, sparse)
        self.conversation_melody_rhythm = [1, 2]
        self.silence_melody_rhythm = [3.5]

        # Rhythm for the "buildup" and "tension" sections (fast, dense)
        self.buildup_melody_rhythm = [0, 1, 1.5, 2, 2.5, 3.5]

        # Rhythm for the chords. We'll use a simple "one-per-bar" for now,
        # but the structure allows for more.
        self.simple_chord_rhythm = [0]
        self.release_chord_rhythm = [0, 2]
        self.buildup_chord_rhythm = [0, 2, 3]

    def generate_narrative(self, key, bars=8):
        """
        Generates a list of Bar objects, each containing a chord and
        the melody notes with their specific rhythms for that bar.
        """
        # The final list of structured bar data
        narrative_data = []

        chords_in_key = key.chords
        notes_in_key = key.notes

        # Generate a completely random chord progression for the entire song
        chord_progression = [random.choice(chords_in_key) for _ in range(bars)]

        # --- Section 1: Conversation (Bars 1-2) ---
        for bar in range(2):
            melody_notes = [(random.choice(notes_in_key), offset) for offset in self.conversation_melody_rhythm]
            chords = [(chord_progression[bar], offset) for offset in self.simple_chord_rhythm]
            narrative_data.append(Bar(chords, melody_notes))

        # --- Section 2: Silence (Bar 3) ---
        melody_notes = [(random.choice(notes_in_key), offset) for offset in self.silence_melody_rhythm]
        chords = [(chord_progression[2], offset) for offset in self.simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 3: Conversation (Bar 4) ---
        melody_notes = [(random.choice(notes_in_key), offset) for offset in self.conversation_melody_rhythm]
        chords = [(chord_progression[3], offset) for offset in self.simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 4: Silence (Bar 5) ---
        melody_notes = [(random.choice(notes_in_key), offset) for offset in self.silence_melody_rhythm]
        chords = [(chord_progression[4], offset) for offset in self.simple_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        # --- Section 5: Buildup & Tension (Bars 6-7) ---
        for bar in range(2):
            melody_notes = [(random.choice(notes_in_key), offset) for offset in self.buildup_melody_rhythm]
            chords = [(chord_progression[5 + bar], offset) for offset in self.buildup_chord_rhythm]
            narrative_data.append(Bar(chords, melody_notes))

        # --- Section 6: Release (Bar 8) ---
        melody_notes = [(random.choice(notes_in_key), 0)]
        chords = [(chord_progression[7], offset) for offset in self.release_chord_rhythm]
        narrative_data.append(Bar(chords, melody_notes))

        return narrative_data, make_signature_key(narrative_data)
