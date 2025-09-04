import random


class Bar:
    def __init__(self, chord, melody_notes):
        self.chord = chord
        self.melody_notes = melody_notes


def make_signature_key(narrative_data: [Bar] = None):
    if narrative_data is None:
        return None
    key = ""
    for data in narrative_data:
        bar_data: Bar = data
        key += empty_replace(bar_data.chord, "_chord")

        for note, rhythm in bar_data.melody_notes:
            key += empty_replace(note, "_note")

    return key


def empty_replace(s: str, p: str):
    return s.replace(p, "")


# --- Music Theory Setup (reused from our previous discussions) ---
# A list of available chords and notes to choose from randomly.
AVAILABLE_CHORDS = ['C_maj_chord', 'G_maj_chord']
AVAILABLE_NOTES = ['C_note', 'E_note', 'G_note', 'C5_note']


class NarrativeGenerator:
    """
    Generates a melody and rhythm based on a musical narrative,
    returning a structured list of bars.
    """

    def __init__(self):
        # Rhythm for the "conversation" sections (simple, sparse)
        self.conversation_rhythm = [1.5, 2.5, 3, 3.5]
        self.silence_rhythm = [2, 3.5]

        # Rhythm for the "buildup" and "tension" sections (fast, dense)
        self.buildup_rhythm = [0, 1, 1.5, 2, 2.5, 3.5]

    def generate_narrative(self, bars=8):
        """
        Generates a list of Bar objects, each containing a chord and
        the melody notes with their specific rhythms for that bar.
        """
        # The final list of structured bar data
        narrative_data = []

        # Generate a completely random chord progression for the entire song
        chord_progression = [random.choice(AVAILABLE_CHORDS) for _ in range(bars)]

        # --- Section 1: Conversation (Bars 1-2) ---
        # print("Generating: Conversation (Bars 1-2)")
        for bar in range(2):
            melody_notes = []
            for offset in self.conversation_rhythm:
                melody_notes.append((random.choice(AVAILABLE_NOTES), offset))
            narrative_data.append(Bar(chord_progression[bar], melody_notes))

        # --- Section 2: Silence (Bar 3) ---
        # print("Generating: Silence (Bar 3)")
        melody_notes = []
        for offset in self.silence_rhythm:
            melody_notes.append((random.choice(AVAILABLE_NOTES), offset))
        narrative_data.append(Bar(chord_progression[2], melody_notes))  # silence

        # --- Section 3: Conversation (Bar 4) ---
        # print("Generating: Conversation (Bar 4)")
        melody_notes = []
        for offset in self.conversation_rhythm:
            melody_notes.append((random.choice(AVAILABLE_NOTES), offset))
        narrative_data.append(Bar(chord_progression[3], melody_notes))

        # --- Section 4: Silence (Bar 5) ---
        # print("Generating: Silence (Bar 5)")
        melody_notes = []
        for offset in self.silence_rhythm:
            melody_notes.append((random.choice(AVAILABLE_NOTES), offset))
        narrative_data.append(Bar(chord_progression[2], melody_notes))  # silence  # Empty melody list for silence

        # --- Section 5: Buildup & Tension (Bars 6-7) ---
        # print("Generating: Buildup & Tension (Bars 6-7)")
        for bar in range(2):
            melody_notes = []
            for offset in self.buildup_rhythm:
                melody_notes.append((random.choice(AVAILABLE_NOTES), offset))
            narrative_data.append(Bar(chord_progression[5 + bar], melody_notes))

        # --- Section 6: Release (Bar 8) ---
        # print("Generating: Release (Bar 8)")
        melody_notes = [(random.choice(AVAILABLE_NOTES), 0)]  # A single note on the first beat
        narrative_data.append(Bar(chord_progression[7], melody_notes))

        return narrative_data, make_signature_key(narrative_data)
