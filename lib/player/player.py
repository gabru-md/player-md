import json
import time
from enum import Enum
from lib.player.sample_loader import load_samples

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
            sample_config (str): The path to the JSON file with sample mappings.
        """
        self.bpm = bpm
        self.beat_duration_ms = (60 / bpm) * 1000
        self.phase_shift_beats = 0

        self.start_mixer()

        # Create separate channels to allow chords and melodies to play simultaneously.
        self.chords_channel = pygame.mixer.Channel(Channels.CHORDS_CHANNEL.value)
        self.melody_channel = pygame.mixer.Channel(Channels.MELODY_CHANNEL.value)
        self.samples = load_samples(sample_config)

        self.history = {}
        self.currently_playing = None
        self.currently_playing_key = None

    def set_phase_shift(self, shift_in_beats):
        """Allows for a global timing shift, useful for syncing."""
        self.phase_shift_beats = shift_in_beats

    def play_music(self, narrative_data, signature_key=None, metadata=None):
        """
        Plays the generated music by iterating through the structured narrative data.

        This function is the main playback engine. It iterates through the
        list of `Bar` objects and schedules each note and chord with precise timing.

        Args:
            narrative_data: A list of Bar objects containing chord and melody info.
            signature_key: signature of the song
        """
        print(f"Playing {signature_key} at {self.bpm} BPM...")

        self.currently_playing = signature_key
        if metadata:
            if 'key' in metadata:
                self.currently_playing_key = metadata['key']

        start_time_ms = pygame.time.get_ticks()

        # To manage both chord and melody timing, we will flatten both into a single,
        # chronologically sorted list of events.
        event_list = []
        for bar_index, bar_data in enumerate(narrative_data):
            bar_start_beat = bar_index * 4

            # Add all chord events for this bar to the event list
            # We now assume bar_data.chords is a list of tuples: [('chord_name', beat_offset)]
            for chord_name, beat_offset in bar_data.chords:
                event_list.append({
                    'type': 'chord',
                    'name': chord_name,
                    'beat_time': bar_start_beat + beat_offset
                })

            # Add all melody events for this bar to the event list
            # We assume bar_data.melody_notes is a list of tuples: [('note_name', beat_offset)]
            for note_name, beat_offset in bar_data.melody_notes:
                event_list.append({
                    'type': 'melody',
                    'name': note_name,
                    'beat_time': bar_start_beat + beat_offset
                })

        # Sort all events by their beat time to ensure correct playback order
        event_list.sort(key=lambda x: x['beat_time'])

        # Now iterate through the sorted events and play them
        for event in event_list:
            expected_play_time_ms = start_time_ms + (event['beat_time'] * self.beat_duration_ms)

            time_to_wait = expected_play_time_ms - pygame.time.get_ticks()
            if time_to_wait > 0:
                pygame.time.wait(int(time_to_wait))

            sound = self.samples.get(event['name'])
            if sound:
                if event['type'] == 'chord':
                    self.melody_channel.stop() # to counter overlap
                    self.chords_channel.play(sound)
                    # print(f"Chord: {event['name']}")
                else:
                    self.melody_channel.stop() # to counter overlap
                    self.melody_channel.play(sound)
                    # print(f"  Note: {event['name']}")

        # Add a final wait at the end of the song to ensure all notes are played
        total_beats = len(narrative_data) * 4
        final_wait_time = start_time_ms + (total_beats * self.beat_duration_ms) - pygame.time.get_ticks()
        if final_wait_time > 0:
            pygame.time.wait(int(final_wait_time))

        if signature_key:
            if signature_key in self.history:
                self.history[signature_key]['played'] += 1
            else:
                self.history[signature_key] = {'played': 1, 'liked': False, 'disliked': False}

        self.currently_playing = None
        self.currently_playing_key = None

    def save_history(self, file_name=None):
        if file_name is None:
            file_name = f"history/{time.time()}.json"
        with open(file_name, 'w') as history_file:
            json.dump(self.history, history_file)
        print(f"History saved to {file_name}")

    def stop_mixer(self):
        pygame.mixer.quit()

    def start_mixer(self):
        pygame.mixer.init()

    def like(self, signature_key):
        if signature_key in self.history:
            self.history[signature_key]['liked'] = True
            self.history[signature_key]['disliked'] = False

    def dislike(self, signature_key):
        if signature_key in self.history:
            self.history[signature_key]['disliked'] = True
            self.history[signature_key]['liked'] = False
