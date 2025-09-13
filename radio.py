from lib.log import Logger
from lib.media.media_info import MediaInfo
from lib.media.media_provider import MediaProvider
from lib.player.player import Player
import argparse
from server.server import create_app

log = Logger.get_log("Radio")


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
    parser.add_argument("--bass", action="store_true", help="Enable bass to be played along with narrative")
    parser.add_argument("--debug", action="store_true", help="Enable debug on flask")

    args = parser.parse_args()

    media_provider = MediaProvider(narratives=args.narratives, keys_str=args.keys, bars=args.bars,
                                   enable_drums=args.drums, max_queue_length=10)
    media_provider.start_producer_thread()

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
            played_so_far = 0
            total_number_of_plays = args.narratives * args.repeat * len(media_provider.key_classes)
            # keep running the cycle of repeating narratives
            while True:
                media_info: MediaInfo = media_provider.get_next_media_info()
                metadata = {'key': media_info.musical_key}
                for _ in range(args.repeat):
                    # this is a thread blocking call
                    player.play_music(narrative_data=media_info.narrative_data,
                                      signature_key=media_info.signature_key,
                                      metadata=metadata)

                    # log how many times the media is played
                    log.info(f"[{played_so_far + 1}/{total_number_of_plays}] played")
                    played_so_far += 1

        except InterruptedError as e:
            log.exception(e)
            raise e
        finally:
            # always save the history
            player.save_history(history_file_name)
            player.stop_mixer()

    if args.ui:
        app = create_app(player=player, player_task=player_task, radio_stats=radio_stats)
        app.run(host='0.0.0.0', port=5000, debug=args.debug)
    else:
        player_task()


if __name__ == '__main__':
    main()
