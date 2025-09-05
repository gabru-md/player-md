import json
import os
import threading
from crypt import methods

from lib.player.player import Player
from flask import Flask, render_template, request

from lib.signature import parse_signature_key


def create_app(player: Player, player_task=None):
    history_folder = "history"
    player_task = player_task
    player = player
    app = Flask(__name__)

    @app.route("/")
    def home():
        all_json_history = {}
        for file in os.listdir(history_folder):
            if file.endswith(".json"):
                with open(os.path.join(history_folder, file)) as json_history_file:
                    # check if history looks like: {'song_signature': {'played': 1, 'liked': False, 'disliked': False}}
                    try:
                        history_from_file = json.load(json_history_file)
                        for song_signature, data in history_from_file.items():
                            if song_signature in all_json_history:
                                # If the song exists, combine the data
                                all_json_history[song_signature]['played'] += data.get('played', 0)
                                all_json_history[song_signature]['liked'] = all_json_history[song_signature].get(
                                    'liked', False) or data.get('liked', False)
                                all_json_history[song_signature]['disliked'] = all_json_history[song_signature].get(
                                    'disliked', False) or data.get('disliked', False)
                            else:
                                # If the song is new, add it to the history
                                all_json_history[song_signature] = data
                    except Exception as e:
                        print(e)

        sorted_history = sorted(
            all_json_history.items(),
            key=lambda item: (item[1].get('liked', False), item[1].get('played', 0)),
            reverse=True
        )

        number_of_songs_to_display = 15
        top_n_history = dict(sorted_history[:number_of_songs_to_display])

        current_history = player.history
        currently_playing = player.currently_playing
        currently_playing_key = player.currently_playing_key.__class__.__name__

        return render_template('home.html', history=top_n_history, current_history=current_history,
                               currently_playing=currently_playing, currently_playing_key=currently_playing_key)

    @app.route('/play')
    def play_radio():
        if player_task:
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
                single_player = Player(bpm=player.bpm)
                try:
                    single_player.play_music(narrative_data=narrative_data, signature_key=signature_key, metadata={'key': song_key})
                except Exception as e:
                    print(e)
                    raise e
                finally:
                    single_player.save_history()
                    single_player.stop_mixer()

            player_thread = threading.Thread(target=play_song, daemon=True)
            player_thread.start()
        return "Ok"

    @app.route('/like', methods=['POST'])
    def like():
        json_data = request.json
        signature_key = json_data['key']
        player.like(signature_key)
        return "Ok"

    @app.route('/dislike')
    def dislike():
        json_data = request.json
        signature_key = json_data['key']
        player.dislike(signature_key)
        return "Ok"

    return app
