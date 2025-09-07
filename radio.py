import random

from lib.player.player import Player
from lib.narrative_generator import NarrativeGenerator
import argparse
from lib.keys import get_key_class
from server.server import create_app


def rotate_list_randomly(input_list):
    if not input_list:
        return []

    # Get a random number of rotations, from 1 up to the length of the list
    num_rotations = random.randint(1, len(input_list) - 1)

    # Use list slicing to perform the rotation
    return input_list[num_rotations:] + input_list[:num_rotations]


def get_full_key_name(notation: str) -> str:
    notation = notation.strip()

    # Check for minor chord suffix 'm'
    if notation.endswith('m'):
        chord_type = "Minor"
        note_part = notation[:-1]
    else:
        chord_type = "Major"
        note_part = notation

    full_note_name = note_part.replace('#', 'Sharp').replace('b', 'Flat')

    full_note_name = full_note_name.capitalize()

    return f"{full_note_name}{chord_type}"


def get_keys_to_play(keys_str):
    harmonic_key_order = [
        'C',
        'Am',
        'G',
        'Em',
        'D',
        'Bm',
        'A',
        'F#m',
        'E',
        'C#m',
        'B',
        'G#m',
        'F#',
        'D#m',
        'C#',
        'A#m',
        'G#',
        'Fm',
        'Eb',
        'Cm',
        'Bb',
        'Gm',
        'F',
        'Dm',
    ]

    if keys_str == 'harmonious' or keys_str == 'fifths':
        keys = rotate_list_randomly(harmonic_key_order)
    else:
        keys = keys_str.split(',')

    keys_to_play = []
    for key in keys:
        full_key_name = get_full_key_name(key)
        key_class = get_key_class(full_key_name)
        if key_class is not None:
            keys_to_play.append(key_class)

    return keys_to_play

def main():
    parser = argparse.ArgumentParser(description="Generate and play music with custom settings.")
    parser.add_argument("--bars", type=int, default=8, help="The number of bars in the generated song.")
    parser.add_argument("--bpm", type=int, default=124, help="The tempo of the music in beats per minute.")
    parser.add_argument("--narratives", type=int, default=1, help="Number of narratives to play")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat a narrative")
    parser.add_argument("--cycle", type=int, default=1, help="Number of times to cycle over scale progression")
    parser.add_argument("--history", type=str, default=None, help="Name of the history file to save the tracks")
    parser.add_argument("--ui", action="store_true", help="Enable web ui using flask")
    parser.add_argument("--keys", type=str, default="C,G,E,G", help="Keys that you want to play (in order)")
    parser.add_argument("--drums", action="store_true", help="Enable drums to be played along with narrative")

    args = parser.parse_args()

    generator = NarrativeGenerator()
    player = Player(bpm=args.bpm)

    radio_stats = {
        'bpm': args.bpm,
        'narratives': args.narratives,
        'repeat': args.repeat,
        'musical_keys': args.keys,
        'drums': args.drums
    }

    def player_task():
        history_file_name = f"history/{args.history}.json" if args.history is not None else None
        try:
            player.start_mixer()
            for _ in range(args.cycle):
                keys_to_play = get_keys_to_play(args.keys)
                for key in [k() for k in keys_to_play]:
                    for _ in range(args.narratives):
                        narrative_data, signature_key = generator.generate_narrative(key=key, bars=8, enable_drums=args.drums)
                        for _ in range(args.repeat):
                            metadata = {'key': key}
                            player.play_music(narrative_data=narrative_data, signature_key=signature_key,
                                              metadata=metadata)
        except InterruptedError as e:
            print(e)
            raise e
        finally:
            player.save_history(history_file_name)
            player.stop_mixer()

    if args.ui:
        app = create_app(player=player, player_task=player_task, radio_stats=radio_stats)
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        player_task()


if __name__ == '__main__':
    main()
