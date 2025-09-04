from player import Player
from narrative_generator import NarrativeGenerator


def main():
    generator = NarrativeGenerator()
    player = Player(bpm=120)

    while True:
        try:
            narrative_data, signature_key = generator.generate_narrative(bars=8)
            for _ in range(4):
                player.play_music(narrative_data=narrative_data, signature_key=signature_key)
        except InterruptedError as e:
            print(e)
            break


if __name__ == '__main__':
    main()
