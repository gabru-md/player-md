import random
from lib.bar import Bar
from lib.player.sample_loader import load_samples
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
            [0],
            [1, 2, 2, 5]
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
            [0, 2],
            [1, 2]
            # [0, 1, 1.5, 2, 2.5, 3]
        ]

        self.drums_rhythm = [
            # kick , hi hat
            ([0, 1, 2, 3], [0.25, 0.75, 1.50, 2.50, 3.50]),
            ([0, 2], [1, 3]),
            ([], [0, 1, 2, 3])
        ]

    def generate_narrative(self, key, bars=8, enable_drums=True):
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

        drums = None
        if enable_drums:
            kick_rhythm, hi_hats_rhythm = random.choice(self.drums_rhythm)
            kicks = [('Kick', offset) for offset in kick_rhythm]
            hi_hats = [('HiHat', offset) for offset in hi_hats_rhythm]
            drums = (kicks, hi_hats)

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
            bass_line = convert_chords_into_bass_line(chords)
            narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        # --- Section 2: Silence (Bar 3) ---
        melody_rhythm = random.choice(self.silence_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[2], offset) for offset in simple_chord_rhythm]
        bass_line = convert_chords_into_bass_line(chords)
        narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        # --- Section 3: Conversation (Bar 4) ---
        melody_rhythm = random.choice(self.rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[3], offset) for offset in simple_chord_rhythm]
        bass_line = convert_chords_into_bass_line(chords)
        narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        # --- Section 4: Silence (Bar 5) ---
        melody_rhythm = random.choice(self.silence_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        simple_chord_rhythm = random.choice(self.simple_chord_rhythm_patterns)
        chords = [(chord_progression[4], offset) for offset in simple_chord_rhythm]
        bass_line = convert_chords_into_bass_line(chords)
        narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        # --- Section 5: Buildup & Tension (Bars 6-7) ---
        for bar in range(2):
            melody_rhythm = random.choice(self.buildup_rhythm_patterns)
            melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
            buildup_chord_rhythm = random.choice(self.buildup_chord_rhythm_patterns)
            chords = [(chord_progression[5 + bar], offset) for offset in buildup_chord_rhythm]
            bass_line = convert_chords_into_bass_line(chords)
            narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        # --- Section 6: Release (Bar 8) ---
        melody_rhythm = random.choice(self.release_rhythm_patterns)
        melody_notes = [(random.choice(notes_in_key), offset) for offset in melody_rhythm]
        release_chord_rhythm = random.choice(self.release_chord_rhythm_patterns)
        chords = [(chord_progression[7], offset) for offset in release_chord_rhythm]
        bass_line = convert_chords_into_bass_line(chords)
        narrative_data.append(Bar(chords, melody_notes, drums=drums, bass=bass_line))

        return narrative_data, make_signature_key(narrative_data)

def convert_chords_into_bass_line(chords):
    bass_line = []
    for chord, offset in chords:
        bass_note = get_bass_note(chord)
        if bass_note:
            bass_line.append((bass_note, offset))
    return bass_line

def get_bass_note(chord):
    key_note = chord.split('_')[0]
    bass_note_key = get_note(key_note, '_bass')
    bass4_note_key = get_note(key_note, '4_bass')

    samples = load_samples("sample_config.json", force_reload=False)

    available_notes = []
    if bass_note_key in samples:
        available_notes.append(bass_note_key)
    if bass4_note_key in samples:
        available_notes.append(bass4_note_key)

    selected_bass_key = random.choice(available_notes)
    return selected_bass_key

def get_note(note, suffix):
    return note + suffix
