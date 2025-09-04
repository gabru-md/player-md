from bar import Bar


def make_signature_key(narrative_data: [Bar] = None):
    """
    Creates a compact signature key from a list of Bar objects.

    The format is: "bar-1_chord_offset:note_offset|bar-2_chord_offset:note_offset"
    This makes the key shorter and more readable.
    """
    if narrative_data is None:
        return None

    key_parts = []
    for bar_data in narrative_data:
        bar_key_parts = []

        # Encode chords and their offsets.
        chord_parts = [f"{empty_replace(c[0], '_chord')}-{float(c[1])}" for c in bar_data.chords]
        if chord_parts:
            bar_key_parts.append(",".join(chord_parts))

        # Encode melody notes and their offsets.
        melody_parts = [f"{empty_replace(m[0], '_note')}-{float(m[1])}" for m in bar_data.melody_notes]
        if melody_parts:
            bar_key_parts.append("|".join(melody_parts))

        key_parts.append(":".join(bar_key_parts))

    return "_^_".join(key_parts)


def empty_replace(s: str, p: str):
    return s.replace(p, "")

def parse_signature_key(key: str) -> list[Bar]:
    """
    Converts a compact signature key string back into a list of Bar objects.
    """
    if not key:
        return []

    narrative_data = []
    bar_strings = key.split('_^_')

    for bar_str in bar_strings:
        parts = bar_str.split(':')
        chords = []
        melody_notes = []

        if len(parts) > 0 and parts[0]:
            chord_str = parts[0].split(',')
            for c in chord_str:
                name, offset = c.rsplit('-', 1)
                chords.append((name + '_chord', float(offset)))

        if len(parts) > 1 and parts[1]:
            melody_str = parts[1].split('|')
            for m in melody_str:
                name, offset = m.rsplit('-', 1)
                melody_notes.append((name + '_note', float(offset)))

        narrative_data.append(Bar(chords, melody_notes))

    return narrative_data