from player import Player
from narrative_generator import NarrativeGenerator
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate and play music with custom settings.")
    parser.add_argument("--bars", type=int, default=8, help="The number of bars in the generated song.")
    parser.add_argument("--bpm", type=int, default=120, help="The tempo of the music in beats per minute.")
    args = parser.parse_args()

    generator = NarrativeGenerator()
    player = Player(bpm=args.bpm)

    try:
        for _ in range(4):
            narrative_data, signature_key = generator.generate_narrative(bars=8) # need to make this configurable or no?
            for _ in range(4):
                player.play_music(narrative_data=narrative_data, signature_key=signature_key)
    except InterruptedError as e:
        print(e)
        raise e
    finally:
        player.save_history()
        player.stop_mixer()


if __name__ == '__main__':
    main()
