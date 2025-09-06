import threading

from lib.player.player import Player
from lib.narrative_generator import NarrativeGenerator
import argparse
from lib.keys import Keys
from server.server import create_app


def main():
    parser = argparse.ArgumentParser(description="Generate and play music with custom settings.")
    parser.add_argument("--bars", type=int, default=8, help="The number of bars in the generated song.")
    parser.add_argument("--bpm", type=int, default=124, help="The tempo of the music in beats per minute.")
    parser.add_argument("--narratives", type=int, default=1, help="Number of narratives to play")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat a narrative")
    parser.add_argument("--cycle", type=int, default=1, help="Number of times to cycle over scale progression")
    parser.add_argument("--history", type=str, default=None, help="Name of the history file to save the tracks")
    parser.add_argument("--ui", action="store_true", help="Enable web ui using flask")
    args = parser.parse_args()

    generator = NarrativeGenerator()
    player = Player(bpm=args.bpm)


    def player_task():
        history_file_name = f"history/{args.history}.json" if args.history is not None else None
        try:
            player.start_mixer()
            for _ in range(args.cycle):
                for key in [k() for k in
                            [Keys.FMinor]]:
                    for _ in range(args.narratives):
                        narrative_data, signature_key = generator.generate_narrative(key=key, bars=8)
                        for _ in range(args.repeat):
                            metadata = {'key': key}
                            player.play_music(narrative_data=narrative_data, signature_key=signature_key, metadata=metadata)
        except InterruptedError as e:
            print(e)
            raise e
        finally:
            player.save_history(history_file_name)
            player.stop_mixer()

    if args.ui:
        app = create_app(player, player_task)
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        player_task()


if __name__ == '__main__':
    main()
