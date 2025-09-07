class Bar:
    def __init__(self, chords, melody_notes, drums=None):
        """
        A single bar of music containing both chord and melody information.

        Args:
            chords (list): A list of tuples, where each tuple is (chord_name, beat_offset).
            melody_notes (list): A list of tuples, where each tuple is (note_name, beat_offset).
        """
        self.chords = chords
        self.melody_notes = melody_notes
        self.drums = drums