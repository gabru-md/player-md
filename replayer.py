import argparse
import json

from player import Player
from lib.signature import parse_signature_key


def main():
    parser = argparse.ArgumentParser(description="Replay a history file")
    parser.add_argument("--file", default="1757020391.8940349", type=str, help="History file you want to replay")
    parser.add_argument('--bpm', default=124, type=int, help="BPM of the player")
    parser.add_argument('-n', type=int, help="Index of single file")

    args = parser.parse_args()

    player = Player(bpm=args.bpm)

    history_file_name = f"history/history_{args.file}.json"

    try:
        history_data = None
        with open(history_file_name, 'r') as history_file:
            history_data = json.load(history_file)
            # update the player's history so it updates
            player.history = history_data

        ordered_history_keys = sorted(history_data.keys())
        idx_key_map = {}
        for idx, key in enumerate(ordered_history_keys):
            print(f"{idx + 1} : {key}")
            idx_key_map[idx + 1] = key

        while True:
            user_input = input("Command: ")

            try:
                command, idx = user_input.split(" ")

                if command == "play":
                    i_idx = int(idx)
                    signature_key = idx_key_map[i_idx]
                    narrative_data = parse_signature_key(signature_key)
                    if narrative_data:
                        player.play_music(narrative_data=narrative_data, signature_key=signature_key)
                if command == "like":
                    i_idx = int(idx)
                    signature_key = idx_key_map[i_idx]
                    player.history[signature_key]['liked'] = True
                if command == "dislike":
                    i_idx = int(idx)
                    signature_key = idx_key_map[i_idx]
                    player.history[signature_key]['disliked'] = True
                if command == "stats":
                    i_idx = int(idx)
                    signature_key = idx_key_map[i_idx]
                    stats = player.history[signature_key]
                    print(stats)

            except Exception as e:
                print(e)
                raise e
    except Exception as e:
        print(e)
        raise e
    finally:
        player.save_history(file_name=history_file_name)
        player.stop_mixer()


if __name__ == '__main__':
    main()
