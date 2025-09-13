import time
from enum import Enum

from lib.history.history_manager import HistoryManager
from lib.log import Logger
from lib.player.sample_loader import load_samples

import pygame

MIXER_RUNNING = False


class Channels(Enum):
    CHORDS_CHANNEL = 0
    MELODY_CHANNEL = 1
    DRUMS_CHANNEL = 2
    BASS_CHANNEL = 4


class Player:
    def __init__(self, name="Radio", bpm=72, sample_config="sample_config.json"):
        """
        Initializes the music player.

        Args:
            bpm (int): Beats per minute for tempo control.
            sample_config (str): The path to the JSON file with sample mappings.
        """
        self.name = name
        self.bpm = bpm
        self.beat_duration_ms = (60 / bpm) * 1000
        self.phase_shift_beats = 0

        self.log = Logger.get_log(f"Player - {name}")

        self.start_mixer()
        # Create separate channels to allow chords and melodies to play simultaneously.
        self.chords_channel = pygame.mixer.Channel(Channels.CHORDS_CHANNEL.value)
        self.melody_channel = pygame.mixer.Channel(Channels.MELODY_CHANNEL.value)
        self.drums_channel = pygame.mixer.Channel(Channels.DRUMS_CHANNEL.value)
        self.bass_channel = pygame.mixer.Channel(Channels.BASS_CHANNEL.value)
        self.samples = load_samples(sample_config)

        self.currently_playing = None
        self.currently_playing_key = None
        self.history_manager = HistoryManager()

        self.pause = False
        self.playing = False

    def play_music(self, narrative_data, signature_key=None, metadata=None):
        """
        Plays the generated music by iterating through the structured narrative data.

        This function is the main playback engine. It iterates through the
        list of `Bar` objects and schedules each note and chord with precise timing.

        Args:
            narrative_data: A list of Bar objects containing chord and melody info.
            signature_key: signature of the song
            metadata: any metadata {}
        """

        if pygame.mixer.get_init() is None:
            self.start_mixer()

        self.currently_playing = signature_key
        if metadata:
            if 'key' in metadata:
                self.currently_playing_key = metadata['key']

        self.log.info(f"Playing {self.currently_playing_key} at {self.bpm} BPM...")

        start_time_ms = pygame.time.get_ticks()

        if type(self.currently_playing_key) == str:
            musical_key = self.currently_playing_key
        else:
            musical_key = self.currently_playing_key.__class__.__name__

        self.history_manager.add_to_history(signature_key=signature_key,
                                            musical_key=musical_key)

        # To manage both chord and melody timing, we will flatten both into a single,
        # chronologically sorted list of events.
        event_list = []
        for bar_index, bar_data in enumerate(narrative_data):

            while self.pause:
                # makes the call blocking
                print("Player is paused")
                self.playing = False
                time.sleep(1)

            self.playing = True
            bar_start_beat = bar_index * 4
            if bar_data.bass:
                for bass_note, beat_offset in bar_data.bass:
                    event_list.append({
                        'type': 'bass',
                        'name': bass_note,
                        'beat_time': bar_start_beat + beat_offset
                    })

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

            if bar_data.drums:
                kicks, hi_hats = bar_data.drums
                if kicks:
                    for _, beat_offset in kicks:
                        event_list.append({
                            'type': 'drum',
                            'name': 'Kick',
                            'beat_time': bar_start_beat + beat_offset
                        })

                if hi_hats:
                    for _, beat_offset in hi_hats:
                        event_list.append({
                            'type': 'drum',
                            'name': 'HiHat',
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
                if event['type'] == 'bass':
                    self.bass_channel.stop()
                    self.bass_channel.play(sound)
                elif event['type'] == 'chord':
                    self.melody_channel.stop()  # to counter overlap
                    self.chords_channel.play(sound)
                    # print(f"Chord: {event['name']}")
                elif event['type'] == 'melody':
                    self.melody_channel.stop()  # to counter overlap
                    self.melody_channel.play(sound)
                    # print(f"  Note: {event['name']}")
                elif event['type'] == 'drum':
                    self.drums_channel.play(sound)
            else:
                pass
                # print(f"{event['name']} Sound not found")

        # Add a final wait at the end of the song to ensure all notes are played
        total_beats = len(narrative_data) * 4
        final_wait_time = start_time_ms + (total_beats * self.beat_duration_ms) - pygame.time.get_ticks()
        if final_wait_time > 0:
            pygame.time.wait(int(final_wait_time))

        self.history_manager.incr_played(signature_key=signature_key)

        self.currently_playing = None
        self.currently_playing_key = None
        self.playing = False

    def save_history(self, file_name=None):
        self.history_manager.save_history(file_name=file_name)

    def stop_mixer(self):
        global MIXER_RUNNING
        if MIXER_RUNNING:
            pygame.mixer.quit()
            MIXER_RUNNING = True

    def start_mixer(self):
        global MIXER_RUNNING
        if not MIXER_RUNNING:
            self.log.info(f"{self.name} starting mixer")
            pygame.mixer.init()
            MIXER_RUNNING = True

    def like(self, signature_key):
        self.history_manager.like(signature_key=signature_key)

    def dislike(self, signature_key):
        self.history_manager.dislike(signature_key=signature_key)

    def set_pause(self):
        self.pause = True

    def set_unpause(self):
        self.pause = False

    def is_playing(self):
        return self.playing
