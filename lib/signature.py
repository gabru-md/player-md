from lib.bar import Bar
import base64
import json


def make_signature_key(narrative_data: [Bar] = None, use_hash=False):
    """
    Creates a compact signature key from a list of Bar objects.

    Args:
        narrative_data: List of Bar objects
        use_hash: If True, returns a base64-encoded hash of the musical structure.
                 If False, returns the compressed string format.
    """
    if narrative_data is None:
        return None

    if use_hash:
        return _make_hash_signature(narrative_data)
    else:
        return _make_compressed_signature(narrative_data)


def _make_hash_signature(narrative_data):
    """Creates a base64-encoded signature from the musical data."""
    # Create a structured representation
    structure = []
    for bar_data in narrative_data:
        bar_struct = {
            'c': [(chord_name_compress(c[0]), float(c[1])) for c in bar_data.chords],
            'm': [(note_name_compress(m[0]), float(m[1])) for m in bar_data.melody_notes]
        }
        structure.append(bar_struct)

    # Convert to JSON and encode
    json_str = json.dumps(structure, separators=(',', ':'), sort_keys=True)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded


def _make_compressed_signature(narrative_data):
    """Creates a compressed string signature with abbreviated chord/note names."""
    key_parts = []
    for bar_data in narrative_data:
        bar_parts = []

        # Compress chords
        if bar_data.chords:
            chord_parts = [f"{chord_name_compress(c[0])}{format_offset(c[1])}"
                           for c in bar_data.chords]
            bar_parts.append(",".join(chord_parts))

        # Compress melody notes
        if bar_data.melody_notes:
            melody_parts = [f"{note_name_compress(m[0])}{format_offset(m[1])}"
                            for m in bar_data.melody_notes]
            bar_parts.append("|".join(melody_parts))

        key_parts.append(":".join(bar_parts))

    return "^".join(key_parts)


def chord_name_compress(chord_name):
    """Compress chord names to single characters or short codes."""
    # Remove '_chord' suffix
    name = chord_name.replace('_chord', '')

    # Chord compression mapping
    chord_map = {
        'A_maj': 'A', 'A_min': 'a',
        'B_maj': 'B', 'B_min': 'b',
        'C_maj': 'C', 'C_min': 'c',
        'D_maj': 'D', 'D_min': 'd',
        'E_maj': 'E', 'E_min': 'e',
        'F_maj': 'F', 'F_min': 'f',
        'G_maj': 'G', 'G_min': 'g',
        'CSharp_maj': 'C#', 'CSharp_min': 'c#',
        'DSharp_maj': 'D#', 'DSharp_min': 'd#',
        'FSharp_maj': 'F#', 'FSharp_min': 'f#',
        'GSharp_maj': 'G#', 'GSharp_min': 'g#',
        'ASharp_maj': 'A#', 'ASharp_min': 'a#',
        'EFlat_maj': 'Eb', 'EFlat_min': 'eb',
        'BFlat_maj': 'Bb', 'BFlat_min': 'bb',
        'AFlat_maj': 'Ab', 'AFlat_min': 'ab',
    }

    return chord_map.get(name, name[:3])  # Fallback to first 3 chars


def note_name_compress(note_name):
    """Compress note names to single characters."""
    # Remove '_note' suffix
    name = note_name.replace('_note', '')

    # Note compression mapping
    note_map = {
        'CSharp': 'C#', 'DSharp': 'D#', 'FSharp': 'F#',
        'GSharp': 'G#', 'ASharp': 'A#',
        'CSharp5': 'C5', 'DSharp5': 'D5', 'FSharp5': 'F5',
        'GSharp5': 'G5', 'ASharp5': 'A5',
        'E5': 'E5', 'B5': 'B5'  # Keep octave numbers for clarity
    }

    return note_map.get(name, name)


def format_offset(offset):
    """Format offset as compact as possible."""
    if offset == int(offset):
        return f"@{int(offset)}"
    else:
        return f"@{offset:.1f}"


def parse_signature_key(key: str, is_hash=None) -> list[Bar]:
    """
    Converts a signature key back into a list of Bar objects.

    Args:
        key: The signature key string
        is_hash: If None, auto-detects format. If True/False, forces parsing method.
    """
    if not key:
        return []

    # Auto-detect format if not specified
    if is_hash is None:
        is_hash = _is_hash_format(key)

    if is_hash:
        return _parse_hash_signature(key)
    else:
        return _parse_compressed_signature(key)


def _is_hash_format(key):
    """Detect if the key is in hash format (base64)."""
    try:
        # Try to decode as base64
        decoded = base64.b64decode(key.encode())
        json.loads(decoded.decode())
        return True
    except:
        return False


def _parse_hash_signature(key):
    """Parse a hash-based signature key."""
    try:
        decoded = base64.b64decode(key.encode()).decode()
        structure = json.loads(decoded)

        narrative_data = []
        for bar_struct in structure:
            chords = [(chord_name_expand(c[0]), c[1]) for c in bar_struct.get('c', [])]
            melody_notes = [(note_name_expand(m[0]), m[1]) for m in bar_struct.get('m', [])]
            narrative_data.append(Bar(chords, melody_notes))

        return narrative_data
    except:
        return []


def _parse_compressed_signature(key):
    """Parse a compressed string signature."""
    narrative_data = []
    bar_strings = key.split('^')

    for bar_str in bar_strings:
        parts = bar_str.split(':')
        chords = []
        melody_notes = []

        # Parse chords
        if len(parts) > 0 and parts[0]:
            chord_strs = parts[0].split(',')
            for chord_str in chord_strs:
                if '@' in chord_str:
                    name, offset = chord_str.rsplit('@', 1)
                    chords.append((chord_name_expand(name), float(offset)))

        # Parse melody notes
        if len(parts) > 1 and parts[1]:
            melody_strs = parts[1].split('|')
            for melody_str in melody_strs:
                if '@' in melody_str:
                    name, offset = melody_str.rsplit('@', 1)
                    melody_notes.append((note_name_expand(name), float(offset)))

        narrative_data.append(Bar(chords, melody_notes))

    return narrative_data


def chord_name_expand(compressed_name):
    """Expand compressed chord names back to original format."""
    # Reverse mapping for chords
    expand_map = {
        'A': 'A_maj_chord', 'a': 'A_min_chord',
        'B': 'B_maj_chord', 'b': 'B_min_chord',
        'C': 'C_maj_chord', 'c': 'C_min_chord',
        'D': 'D_maj_chord', 'd': 'D_min_chord',
        'E': 'E_maj_chord', 'e': 'E_min_chord',
        'F': 'F_maj_chord', 'f': 'F_min_chord',
        'G': 'G_maj_chord', 'g': 'G_min_chord',
        'C#': 'CSharp_maj_chord', 'c#': 'CSharp_min_chord',
        'D#': 'DSharp_maj_chord', 'd#': 'DSharp_min_chord',
        'F#': 'FSharp_maj_chord', 'f#': 'FSharp_min_chord',
        'G#': 'GSharp_maj_chord', 'g#': 'GSharp_min_chord',
        'A#': 'ASharp_maj_chord', 'a#': 'ASharp_min_chord',
        'Eb': 'EFlat_maj_chord', 'eb': 'EFlat_min_chord',
        'Bb': 'BFlat_maj_chord', 'bb': 'BFlat_min_chord',
        'Ab': 'AFlat_maj_chord', 'ab': 'AFlat_min_chord',
    }

    return expand_map.get(compressed_name, compressed_name + '_chord')


def note_name_expand(compressed_name):
    """Expand compressed note names back to original format."""
    # Reverse mapping for notes
    expand_map = {
        'C#': 'CSharp_note', 'D#': 'DSharp_note', 'F#': 'FSharp_note',
        'G#': 'GSharp_note', 'A#': 'ASharp_note',
        'C5': 'CSharp5_note', 'D5': 'DSharp5_note', 'F5': 'FSharp5_note',
        'G5': 'GSharp5_note', 'A5': 'ASharp5_note',
        'E5': 'E5_note', 'B5': 'B5_note'
    }

    return expand_map.get(compressed_name, compressed_name + '_note')


# Utility function to estimate compression ratio


def _make_original_signature(narrative_data):
    """Recreate the original signature format for comparison."""
    key_parts = []
    for bar_data in narrative_data:
        bar_key_parts = []

        chord_parts = [f"{bar_data.chords[i][0].replace('_chord', '')}-{float(bar_data.chords[i][1])}"
                       for i in range(len(bar_data.chords))]
        if chord_parts:
            bar_key_parts.append(",".join(chord_parts))

        melody_parts = [f"{bar_data.melody_notes[i][0].replace('_note', '')}-{float(bar_data.melody_notes[i][1])}"
                        for i in range(len(bar_data.melody_notes))]
        if melody_parts:
            bar_key_parts.append("|".join(melody_parts))

        key_parts.append(":".join(bar_key_parts))

    return "_^_".join(key_parts)