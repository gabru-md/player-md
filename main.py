from player import Player
from lib.narrative_generator import NarrativeGenerator
import argparse
from lib.keys import Keys


def main():
    parser = argparse.ArgumentParser(description="Generate and play music with custom settings.")
    parser.add_argument("--bars", type=int, default=8, help="The number of bars in the generated song.")
    parser.add_argument("--bpm", type=int, default=124, help="The tempo of the music in beats per minute.")
    parser.add_argument("--narratives", type=int, default=1, help="Number of narratives to play")
    parser.add_argument("--repeat", type=int, default=1, help="Number of times to repeat a narrative")
    parser.add_argument("--cycle", type=int, default=1, help="Number of times to cycle over scale progression")
    args = parser.parse_args()

    generator = NarrativeGenerator()
    player = Player(bpm=args.bpm)

    try:
        for _ in range(args.cycle):
            for key in [k() for k in [Keys.CMajor, Keys.GMajor, Keys.EMinor, Keys.BMinor, Keys.EMinor, Keys.CMajor]]:
                for _ in range(args.narratives):
                    narrative_data, signature_key = generator.generate_narrative(key=key, bars=8)
                    for _ in range(args.repeat):
                        player.play_music(narrative_data=narrative_data, signature_key=signature_key)
    except InterruptedError as e:
        print(e)
        raise e
    finally:
        player.save_history()
        player.stop_mixer()


if __name__ == '__main__':
    main()
