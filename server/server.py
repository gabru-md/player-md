import threading
import time

from lib.player.player import Player
from flask import Flask, render_template, request

from lib.media.narrative.signature import parse_signature_key


def create_app(player: Player, replayer: Player = None, player_task=None, radio_stats=None):
    if radio_stats is None:
        radio_stats = {}
    player_task = player_task
    player = player
    if replayer is None:
        replayer = Player(name="Replayer", bpm=player.bpm)
    app = Flask(__name__)

    @app.route("/")
    def home():
        all_json_history = player.history_manager.load_history()
        all_history_size = 0

        if all_json_history is not None:
            sorted_history = sorted(
                all_json_history.items(),
                key=lambda item: item[1].get('lastPlayed'),
                reverse=True
            )
            all_history_size = len(all_json_history)
            number_of_songs_to_display = 15
            top_n_history = dict(sorted_history[:number_of_songs_to_display])
        else:
            top_n_history = {}

        current_history = player.history_manager.history
        currently_playing = player.currently_playing
        player_name = player.name

        radio_stats.update({
            'name': player.name,
            'bpm': player.bpm,
            'pause': player.pause,
            'playing': player.playing
        })

        if player.pause and not player.playing:
            current_history = replayer.history_manager.history
            currently_playing = replayer.currently_playing
            currently_playing_key = replayer.currently_playing_key
            player_name = replayer.name

            radio_stats.update({
                'name': replayer.name,
                'bpm': replayer.bpm,
                'pause': replayer.pause,
                'playing': replayer.playing
            })

        else:
            currently_playing_key = player.currently_playing_key.__class__.__name__
            radio_stats.update({
                'name': player.name,
                'bpm': player.bpm,
                'pause': player.pause,
                'playing': player.playing
            })

        return render_template('home.html', history=top_n_history, all_history_size=all_history_size,
                               current_history=current_history,
                               currently_playing=currently_playing, currently_playing_key=currently_playing_key,
                               player_name=player_name, radio_stats=radio_stats)

    @app.route('/play')
    def play_radio():
        if player_task:
            player.start_mixer()
            player_thread = threading.Thread(target=player_task, daemon=True)
            player_thread.start()
        return "Ok"

    @app.route('/replay', methods=['POST'])
    def play_single_song():
        json_data = request.json
        signature_key = json_data['key']
        song_key = json_data['song_key']
        if signature_key:
            narrative_data = parse_signature_key(signature_key)

            def play_song():
                try:
                    while replayer.is_playing():
                        print("Waiting for replayer to finish")
                        time.sleep(1)
                    player.set_pause()
                    while player.is_playing():
                        print("Waiting for Main player to pause")
                        time.sleep(1)
                    replayer.start_mixer()
                    replayer.play_music(narrative_data=narrative_data, signature_key=signature_key,
                                        metadata={'key': song_key})
                except Exception as e:
                    print(e)
                    raise e
                finally:
                    replayer.save_history()
                    time.sleep(2)
                    player.set_unpause()

            player_thread = threading.Thread(target=play_song, daemon=True)
            player_thread.start()
        return "Ok"

    @app.route('/like', methods=['POST'])
    def like():
        json_data = request.json
        signature_key = json_data['key']
        player.like(signature_key)
        return "Ok"

    @app.route('/dislike', methods=['POST'])
    def dislike():
        json_data = request.json
        signature_key = json_data['key']
        player.dislike(signature_key)
        return "Ok"

    return app
