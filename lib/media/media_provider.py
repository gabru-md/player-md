import random
import threading
import time
import queue
from lib.keys import Keys
from lib.media.media_info import MediaInfo
from lib.media.narrative.narrative_generator import NarrativeGenerator
from lib.log import Logger

PRODUCER_SLEEP_TIME = 30  # seconds


def get_keys(keys_str):
    harmonic_key_order = [
        'C', 'Am', 'G', 'Em', 'D', 'Bm', 'A', 'F#m', 'E', 'C#m', 'B', 'G#m',
        'F#', 'D#m', 'C#', 'A#m', 'G#', 'Fm', 'Eb', 'Cm', 'Bb', 'Gm', 'F', 'Dm',
    ]
    if keys_str == 'harmonious' or keys_str == 'fifths':
        keys = rotate_list_randomly(harmonic_key_order)
    else:
        keys = keys_str.split(',')
    keys_to_play = []
    for key in keys:
        full_key_name = get_full_key_name(key)
        key_class = Keys.get_key_class(full_key_name)
        if key_class is not None:
            keys_to_play.append(key_class)
    return keys_to_play


def rotate_list_randomly(input_list):
    if not input_list:
        return []
    num_rotations = random.randint(1, len(input_list) - 1)
    return input_list[num_rotations:] + input_list[:num_rotations]


def get_full_key_name(notation: str) -> str:
    notation = notation.strip()
    if notation.endswith('m'):
        chord_type = "Minor"
        note_part = notation[:-1]
    else:
        chord_type = "Major"
        note_part = notation
    full_note_name = note_part.replace('#', 'Sharp').replace('b', 'Flat')
    full_note_name = full_note_name.capitalize()
    return f"{full_note_name}{chord_type}"


class MediaProvider:
    def __init__(self, narratives, keys_str, max_queue_length=10):
        self.generator = NarrativeGenerator()
        self.narrative_data_queue = queue.Queue(maxsize=max_queue_length)
        self.key_classes = get_keys(keys_str)
        self.num_of_narratives = narratives

        self.producer_thread = threading.Thread(target=self.produce_media_info, daemon=True)
        self.currently_producing_key_class = None

        self.log = Logger.get_log(self.__class__.__name__)
        self.num_of_narratives_produced = 0
        self.currently_producing_key = None

    def start_producer_thread(self):
        self.producer_thread.start()

    def produce_media_info(self):
        self.log.info("Starting producer thread.")
        while True:
            if self.narrative_data_queue.full():
                self.log.info("Queue is full, waiting for consumer to catch up.")
                time.sleep(PRODUCER_SLEEP_TIME)
                continue

            try:
                while not self.narrative_data_queue.full():
                    self.currently_producing_key_class = self.get_next_key_class()
                    self.currently_producing_key = self.currently_producing_key_class()
                    self.log.info(f"Currently producing {self.currently_producing_key}")
                    narrative_data, signature_key = self.generator.generate(
                        key=self.currently_producing_key,
                        bars=3)

                    self.narrative_data_queue.put(MediaInfo(narrative_data, signature_key))
                    self.num_of_narratives_produced += 1

                self.log.info("Queue is filled back again.")
            except Exception as e:
                self.log.exception(e)
                time.sleep(PRODUCER_SLEEP_TIME)

    def get_next_media_info(self):
        try:
            return self.narrative_data_queue.get(block=False)
        except queue.Empty:
            self.log.info("Narrative data queue is empty.")
            return None

    def get_next_key_class(self):
        current_producing_key_class = self.currently_producing_key_class
        narrative_offset = self.num_of_narratives_produced % self.num_of_narratives
        if narrative_offset == 0:
            return self._get_next_key_class()
        return current_producing_key_class

    def _get_next_key_class(self):
        current_key_idx = -1
        for idx, key in enumerate(self.key_classes):
            if key == self.currently_producing_key_class:
                current_key_idx = idx
                break
        next_key_idx = (current_key_idx + 1) % len(self.key_classes)
        return self.key_classes[next_key_idx]


if __name__ == '__main__':
    mock_keys_str = "C,Am,G"
    provider = MediaProvider(narratives=3, keys_str=mock_keys_str, max_queue_length=5)
    provider.start_producer_thread()

    for _ in range(30):
        media_info = provider.get_next_media_info()
        if media_info:
            print(f"Retrieved media info for key: {media_info.signature_key}")
        else:
            print("No media info available yet. Waiting...")
        time.sleep(5)
