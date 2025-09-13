import json


class _KeyBase:
    """A base class to provide a string representation for all key classes."""
    def __repr__(self):
        return self.__class__.__name__


class Keys:
    class CMajor(_KeyBase):
        def __init__(self):
            self.chords = ['C_maj_chord', 'G_maj_chord', 'A_min_chord', 'F_maj_chord', 'D_min_chord',
                           'E_min_chord']
            self.notes = ['C_note', 'E_note', 'G_note', 'C5_note', 'C_E_slide_note', 'E_G_slide_note']

    class GMajor(_KeyBase):
        def __init__(self):
            self.chords = ['G_maj_chord', 'D_maj_chord', 'E_min_chord', 'C_maj_chord', 'A_min_chord',
                           'B_min_chord']
            self.notes = ['G_note', 'B_note', 'D_note', 'G5_note']

    class AMajor(_KeyBase):
        def __init__(self):
            self.chords = ['A_maj_chord', 'E_maj_chord', 'FSharp_min_chord', 'D_maj_chord', 'B_min_chord',
                           'CSharp_min_chord']
            self.notes = ['A_note', 'CSharp_note', 'E_note', 'A5_note']

    class EMajor(_KeyBase):
        def __init__(self):
            self.chords = ['E_maj_chord', 'B_maj_chord', 'CSharp_min_chord', 'A_maj_chord', 'FSharp_min_chord',
                           'GSharp_min_chord']
            self.notes = ['E_note', 'GSharp_note', 'B_note', 'E5_note']

    class DMajor(_KeyBase):
        def __init__(self):
            self.chords = ['D_maj_chord', 'A_maj_chord', 'B_min_chord', 'G_maj_chord', 'E_min_chord',
                           'FSharp_min_chord']
            self.notes = ['D_note', 'FSharp_note', 'A_note', 'D5_note']

    class FMajor(_KeyBase):
        def __init__(self):
            self.chords = ['F_maj_chord', 'C_maj_chord', 'D_min_chord', 'BFlat_maj_chord', 'G_min_chord',
                           'A_min_chord']
            self.notes = ['F_note', 'A_note', 'C_note', 'F5_note']

    class BMajor(_KeyBase):
        def __init__(self):
            self.chords = ['B_maj_chord', 'FSharp_maj_chord', 'GSharp_min_chord', 'E_maj_chord', 'CSharp_min_chord',
                           'DSharp_min_chord']
            self.notes = ['B_note', 'DSharp_note', 'FSharp_note', 'B5_note']

    class FSharpMajor(_KeyBase):
        def __init__(self):
            self.chords = ['FSharp_maj_chord', 'CSharp_maj_chord', 'DSharp_min_chord', 'B_maj_chord',
                           'GSharp_min_chord', 'ASharp_min_chord']
            self.notes = ['FSharp_note', 'ASharp_note', 'CSharp_note', 'FSharp5_note']

    class CSharpMajor(_KeyBase):
        def __init__(self):
            self.chords = ['CSharp_maj_chord', 'GSharp_maj_chord', 'ASharp_min_chord', 'FSharp_maj_chord',
                           'DSharp_min_chord', 'F_min_chord']
            self.notes = ['CSharp_note', 'F_note', 'GSharp_note', 'CSharp5_note']

    class GSharpMajor(_KeyBase):
        def __init__(self):
            self.chords = ['GSharp_maj_chord', 'DSharp_maj_chord', 'F_min_chord', 'CSharp_maj_chord',
                           'ASharp_min_chord', 'C_min_chord']
            self.notes = ['GSharp_note', 'C_note', 'DSharp_note', 'GSharp5_note']

    class AFlatMajor(_KeyBase):
        def __init__(self):
            self.chords = ['AFlat_maj_chord', 'EFlat_maj_chord', 'F_min_chord', 'DFlat_maj_chord', 'BFlat_min_chord',
                           'C_min_chord']
            self.notes = ['AFlat_note', 'C_note', 'EFlat_note', 'AFlat5_note']

    class DFlatMajor(_KeyBase):
        def __init__(self):
            self.chords = ['DFlat_maj_chord', 'AFlat_maj_chord', 'BFlat_min_chord', 'GFlat_maj_chord',
                           'EFlat_min_chord', 'F_min_chord']
            self.notes = ['DFlat_note', 'F_note', 'AFlat_note', 'DFlat5_note']

    class EFlatMajor(_KeyBase):
        def __init__(self):
            self.chords = ['EFlat_maj_chord', 'BFlat_maj_chord', 'C_min_chord', 'AFlat_maj_chord', 'F_min_chord',
                           'G_min_chord']
            self.notes = ['EFlat_note', 'G_note', 'BFlat_note', 'EFlat5_note']

    class BFlatMajor(_KeyBase):
        def __init__(self):
            self.chords = ['BFlat_maj_chord', 'F_maj_chord', 'G_min_chord', 'EFlat_maj_chord', 'C_min_chord',
                           'D_min_chord']
            self.notes = ['BFlat_note', 'D_note', 'F_note', 'BFlat5_note']

    class AMinor(_KeyBase):
        def __init__(self):
            self.chords = ['A_min_chord', 'E_min_chord', 'F_maj_chord', 'G_maj_chord', 'D_min_chord']
            self.notes = ['A_note', 'C_note', 'E_note', 'A5_note']

    class EMinor(_KeyBase):
        def __init__(self):
            self.chords = ['E_min_chord', 'B_min_chord', 'C_maj_chord', 'D_maj_chord', 'A_min_chord']
            self.notes = ['E_note', 'G_note', 'B_note', 'E5_note']

    class BMinor(_KeyBase):
        def __init__(self):
            self.chords = ['B_min_chord', 'FSharp_min_chord', 'G_maj_chord', 'A_maj_chord', 'E_min_chord']
            self.notes = ['B_note', 'D_note', 'FSharp_note', 'B5_note']

    class FSharpMinor(_KeyBase):
        def __init__(self):
            self.chords = ['FSharp_min_chord', 'CSharp_min_chord', 'D_maj_chord', 'E_maj_chord', 'B_min_chord']
            self.notes = ['FSharp_note', 'A_note', 'CSharp_note', 'FSharp5_note']

    class CSharpMinor(_KeyBase):
        def __init__(self):
            self.chords = ['CSharp_min_chord', 'GSharp_min_chord', 'A_maj_chord', 'B_maj_chord', 'FSharp_min_chord']
            self.notes = ['CSharp_note', 'E_note', 'GSharp_note', 'CSharp5_note']

    class GSharpMinor(_KeyBase):
        def __init__(self):
            self.chords = ['GSharp_min_chord', 'B_maj_chord', 'CSharp_min_chord', 'E_maj_chord', 'FSharp_min_chord']
            self.notes = ['GSharp_note', 'B_note', 'CSharp_note', 'E_note', 'FSharp_note']

    class GMinor(_KeyBase):
        def __init__(self):
            self.chords = ['G_min_chord', 'D_min_chord', 'EFlat_maj_chord', 'F_maj_chord', 'C_min_chord']
            self.notes = ['G_note', 'BFlat_note', 'D_note', 'G5_note']

    class DMinor(_KeyBase):
        def __init__(self):
            self.chords = ['D_min_chord', 'A_min_chord', 'BFlat_maj_chord', 'C_maj_chord', 'G_min_chord']
            self.notes = ['D_note', 'F_note', 'A_note', 'D5_note']

    class CMinor(_KeyBase):
        def __init__(self):
            self.chords = ['C_min_chord', 'G_min_chord', 'AFlat_maj_chord', 'BFlat_maj_chord', 'F_min_chord']
            self.notes = ['C_note', 'EFlat_note', 'G_note', 'C5_note']

    class EFlatMinor(_KeyBase):
        def __init__(self):
            self.chords = ['EFlat_min_chord', 'BFlat_min_chord', 'DFlat_maj_chord', 'CSharp_maj_chord',
                           'AFlat_min_chord']
            self.notes = ['EFlat_note', 'GFlat_note', 'BFlat_note', 'EFlat5_note']

    class BFlatMinor(_KeyBase):
        def __init__(self):
            self.chords = ['BFlat_min_chord', 'F_min_chord', 'GFlat_maj_chord', 'AFlat_maj_chord', 'EFlat_min_chord']
            self.notes = ['BFlat_note', 'DFlat_note', 'F_note', 'BFlat5_note']

    class FMinor(_KeyBase):
        def __init__(self):
            self.chords = ['F_min_chord', 'C_min_chord', 'DFlat_maj_chord', 'EFlat_maj_chord', 'BFlat_min_chord']
            self.notes = ['F_note', 'AFlat_note', 'C_note', 'F5_note']

    class AFlatMinor(_KeyBase):
        def __init__(self):
            self.chords = ['AFlat_min_chord', 'EFlat_min_chord', 'GFlat_maj_chord', 'AFlat_maj_chord',
                           'DFlat_min_chord']
            self.notes = ['AFlat_note', 'B_note', 'EFlat_note', 'AFlat5_note']

    class DFlatMinor(_KeyBase):
        def __init__(self):
            self.chords = ['DFlat_min_chord', 'AFlat_min_chord', 'B_maj_chord', 'B_maj_chord', 'GFlat_min_chord']
            self.notes = ['DFlat_note', 'E_note', 'AFlat_note', 'DFlat5_note']

    def get_all_chords_and_notes(self):
        """
        Gathers all unique chords and notes from all keys.

        This method iterates through all the nested key classes within the Keys class,
        instantiates each one, and adds their chords and notes to respective sets
        to ensure all results are unique.

        Returns:
            tuple: A tuple containing two sets: (set of all unique chords, set of all unique notes).
        """
        all_chords = set()
        all_notes = set()

        # Get a list of all inner classes defined in the Keys class.
        # This approach is dynamic and will work even if you add more keys.
        key_classes = [
            attr for attr in dir(self)
            if not attr.startswith('__') and isinstance(getattr(self, attr), type)
        ]

        for key_class_name in key_classes:
            key_class = getattr(self, key_class_name)
            key_instance = key_class()
            all_chords.update(key_instance.chords)
            all_notes.update(key_instance.notes)

        return all_chords, all_notes

    @classmethod
    def get_key_class(cls, full_key_name):
        key_name = full_key_name.replace(' ', '').lower()

        # Iterate through the attributes of the Keys class
        for attr_name in dir(Keys):
            if not attr_name.startswith('__'):
                attr = getattr(Keys, attr_name)
                # Check if the attribute is a class and its name matches the input
                if isinstance(attr, type) and attr_name.lower() == key_name:
                    return attr
        return None

    @staticmethod
    def get_notes_from_chord(chord_name):
        chord_notes_map = {
            'C_maj_chord': ['C_note', 'E_note', 'G_note'],
            'G_maj_chord': ['G_note', 'B_note', 'D_note'],
            'A_min_chord': ['A_note', 'C_note', 'E_note'],
            'F_maj_chord': ['F_note', 'A_note', 'C_note'],
            'D_min_chord': ['D_note', 'F_note', 'A_note'],
            'E_min_chord': ['E_note', 'G_note', 'B_note'],
            'B_maj_chord': ['B_note', 'DSharp_note', 'FSharp_note'],
            'D_maj_chord': ['D_note', 'FSharp_note', 'A_note'],
            'E_maj_chord': ['E_note', 'GSharp_note', 'B_note'],
            'FSharp_min_chord': ['FSharp_note', 'A_note', 'CSharp_note'],
            'CSharp_min_chord': ['CSharp_note', 'E_note', 'GSharp_note'],
            'GSharp_min_chord': ['GSharp_note', 'B_note', 'CSharp_note'],
            'C_min_chord': ['C_note', 'EFlat_note', 'G_note'],
            'BFlat_maj_chord': ['BFlat_note', 'D_note', 'F_note'],
            'G_min_chord': ['G_note', 'BFlat_note', 'D_note'],

            # Newly added chords
            'ASharp_min_chord': ['ASharp_note', 'CSharp_note', 'F_note'],
            'AFlat_maj_chord': ['AFlat_note', 'C_note', 'EFlat_note'],
            'BFlat_min_chord': ['BFlat_note', 'DFlat_note', 'F_note'],
            'B_min_chord': ['B_note', 'D_note', 'FSharp_note'],
            'DFlat_maj_chord': ['DFlat_note', 'F_note', 'AFlat_note'],
            'DFlat_min_chord': ['DFlat_note', 'FFlat_note', 'AFlat_note'],
            'DSharp_min_chord': ['DSharp_note', 'FSharp_note', 'ASharp_note'],
            'EFlat_maj_chord': ['EFlat_note', 'G_note', 'BFlat_note'],
            'EFlat_min_chord': ['EFlat_note', 'GFlat_note', 'BFlat_note'],
            'FSharp_maj_chord': ['FSharp_note', 'ASharp_note', 'CSharp_note'],
            'GSharp_maj_chord': ['GSharp_note', 'BSharp_note', 'DSharp_note'],
            'F_min_chord': ['F_note', 'AFlat_note', 'C_note'],
            # The AFlat_min_chord, B_maj_chord, and DFlat_min_chord seem to be missing
            'AFlat_min_chord': ['AFlat_note', 'CFlat_note', 'EFlat_note']
        }
        return chord_notes_map.get(chord_name, [])

if __name__ == '__main__':
    with open("sample_config.json") as config:
        config_data = json.load(config)
    chords, notes = Keys().get_all_chords_and_notes()

    if config_data:

        for chord in chords:
            if chord not in config_data:
                print(f"\"{chord}\": \"sample/{chord}.wav\",")

        for note in notes:
            if note not in config_data:
                print(f"\"{note}\": \"sample/{note}.wav\",")

    # print(get_key_class('CMajor'))
    # Example of the new functionality
    c_major_class = Keys.CMajor
    c_major_instance = Keys.CMajor()
    print(c_major_class)
    print(c_major_instance)