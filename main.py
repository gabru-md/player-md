from player import Player
from narrative_generator import NarrativeGenerator


def main():
    generator = NarrativeGenerator()
    player = Player(bpm=80)

    while True:
        try:
            narrative_data = generator.generate_narrative(bars=8)
            player.play_music(narrative_data=narrative_data)
        except InterruptedError as e:
            print(e)
            break


if __name__ == '__main__':
    main()
