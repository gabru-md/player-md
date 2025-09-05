class Keys:
    class CMajor:
        def __init__(self):
            self.chords = ['C_maj_chord', 'G_maj_chord', 'A_min_chord', 'F_maj_chord', 'D_min_chord',
                           'E_min_chord']
            self.notes = ['C_note', 'E_note', 'G_note', 'C5_note', 'C_E_slide_note', 'E_G_slide_note']

    class GMajor:
        def __init__(self):
            self.chords = ['G_maj_chord', 'D_maj_chord', 'E_min_chord', 'C_maj_chord', 'A_min_chord',
                           'B_min_chord']
            self.notes = ['G_note', 'B_note', 'D_note', 'G5_note']

    class AMajor:
        def __init__(self):
            self.chords = ['A_maj_chord', 'E_maj_chord', 'FSharp_min_chord', 'D_maj_chord', 'B_min_chord',
                           'CSharp_min_chord']
            self.notes = ['A_note', 'CSharp_note', 'E_note', 'A5_note']

    class EMajor:
        def __init__(self):
            self.chords = ['E_maj_chord', 'B_maj_chord', 'CSharp_min_chord', 'A_maj_chord', 'FSharp_min_chord',
                           'GSharp_min_chord']
            self.notes = ['E_note', 'GSharp_note', 'B_note', 'E5_note']

    class DMajor:
        def __init__(self):
            self.chords = ['D_maj_chord', 'A_maj_chord', 'B_min_chord', 'G_maj_chord', 'E_min_chord',
                           'FSharp_min_chord']
            self.notes = ['D_note', 'FSharp_note', 'A_note', 'D5_note']

    class FMajor:
        def __init__(self):
            self.chords = ['F_maj_chord', 'C_maj_chord', 'D_min_chord', 'BFlat_maj_chord', 'G_min_chord',
                           'A_min_chord']
            self.notes = ['F_note', 'A_note', 'C_note', 'F5_note']

    class AMinor:
        def __init__(self):
            self.chords = ['A_min_chord', 'E_min_chord', 'F_maj_chord', 'G_maj_chord', 'D_min_chord']
            self.notes = ['A_note', 'C_note', 'E_note', 'A5_note']

    class EMinor:
        def __init__(self):
            self.chords = ['E_min_chord', 'B_min_chord', 'C_maj_chord', 'D_maj_chord', 'A_min_chord']
            self.notes = ['E_note', 'G_note', 'B_note', 'E5_note']

    class BMinor:
        def __init__(self):
            self.chords = ['B_min_chord', 'FSharp_min_chord', 'G_maj_chord', 'A_maj_chord', 'E_min_chord']
            self.notes = ['B_note', 'D_note', 'FSharp_note', 'B5_note']

    class FSharpMinor:
        def __init__(self):
            self.chords = ['FSharp_min_chord', 'CSharp_min_chord', 'D_maj_chord', 'E_maj_chord', 'B_min_chord']
            self.notes = ['FSharp_note', 'A_note', 'CSharp_note', 'FSharp5_note']

    class CSharpMinor:
        def __init__(self):
            self.chords = ['CSharp_min_chord', 'GSharp_min_chord', 'A_maj_chord', 'B_maj_chord', 'FSharp_min_chord']
            self.notes = ['CSharp_note', 'E_note', 'GSharp_note', 'CSharp5_note']

    class GMinor:
        def __init__(self):
            self.chords = ['G_min_chord', 'D_min_chord', 'E_flat_maj_chord', 'F_maj_chord', 'C_min_chord',
                           'A_dim_chord']
            self.notes = ['G_note', 'B_flat_note', 'D_note', 'G5_note']

    class FMinor:
        def __init__(self):
            self.chords = ['F_min_chord', 'G_dim_chord', 'A_flat_maj_chord', 'B_flat_min_chord', 'C_min_chord',
                           'D_flat_maj_chord', 'E_flat_maj_chord']
            self.notes = ['F_note', 'A_flat_note', 'C_note', 'F5_note']
