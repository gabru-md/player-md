from enum import Enum
from sample_loader import load_samples
from audio_compressor import AudioCompressor
import pygame


class Channels(Enum):
    CHORDS_CHANNEL = 0
    MELODY_CHANNEL = 1


class Player:
    def __init__(self, bpm=72, sample_config="sample_config.json"):
        """
        Initializes the music player.

        Args:
            bpm (int): Beats per minute for tempo control.
            bars (int): The total number of bars to play.
            sample_config (str): The path to the JSON file with sample mappings.
        """
        self.bpm = bpm
        self.beat_duration_ms = (60 / bpm) * 1000
        self.phase_shift_beats = 0
        pygame.mixer.init()

        # Create separate channels to allow chords and melodies to play simultaneously.
        self.chords_channel = pygame.mixer.Channel(Channels.CHORDS_CHANNEL.value)
        self.melody_channel = pygame.mixer.Channel(Channels.MELODY_CHANNEL.value)
        self.samples = load_samples(sample_config, AudioCompressor())

        self.history = {}

    def set_phase_shift(self, shift_in_beats):
        """Allows for a global timing shift, useful for syncing."""
        self.phase_shift_beats = shift_in_beats

    def play_music(self, narrative_data, signature_key=None):
        """
        Plays the generated music by iterating through the structured narrative data.

        This function is the main playback engine. It iterates through the
        list of `Bar` objects and schedules each note and chord with precise timing.

        Args:
            narrative_data: A list of Bar objects containing chord and melody info.
            signature_key: signature of the song
        """
        print(f"Playing {signature_key} at {self.bpm} BPM...")
        start_time_ms = pygame.time.get_ticks()

        bar_duration_ms = 4 * self.beat_duration_ms

        for bar_index, bar_data in enumerate(narrative_data):
            # This is the expected start time for the current bar.
            current_bar_start_time = start_time_ms + (bar_index * bar_duration_ms)

            # Wait until it's the correct time for this bar to begin.
            time_to_wait_for_bar = current_bar_start_time - pygame.time.get_ticks()
            if time_to_wait_for_bar > 0:
                pygame.time.wait(int(time_to_wait_for_bar))

            # print(f"Bar: {bar_index + 1}")

            # --- Chord Playback ---
            # Play the chord at the very beginning of the bar.
            chord_sound = self.samples.get(bar_data.chord)
            if chord_sound:
                self.chords_channel.play(chord_sound)
                # print(f"Chord: {bar_data.chord}")

            # --- Melody Playback ---
            # Iterate through the list of melody notes and their offsets for this bar.
            for note_name, beat_offset in bar_data.melody_notes:
                # Calculate the precise time to play the note from the beginning of the song.
                # `(bar_index * 4)` gets the total beats from previous bars.
                # `beat_offset` gets the position within the current bar.
                expected_play_time_ms = start_time_ms + ((bar_index * 4 + beat_offset) * self.beat_duration_ms)

                # Wait until it's time to play the next note.
                time_to_wait = expected_play_time_ms - pygame.time.get_ticks()
                if time_to_wait > 0:
                    pygame.time.wait(int(time_to_wait))

                note_sound = self.samples.get(note_name)
                if note_sound:
                    self.melody_channel.play(note_sound)
                    # print(f"  Note: {note_name}")


        if signature_key:
            if signature_key in self.history:
                self.history[signature_key]['played'] += 1
            else:
                self.history[signature_key] = {'played': 0, 'liked':False, 'disliked': False}


            print(self.history)

