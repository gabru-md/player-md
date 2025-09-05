import json
import os
import threading
from crypt import methods

from lib.player.player import Player
from flask import Flask, render_template, request


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
                    all_json_history.update(json.load(json_history_file))

        sorted_history = sorted(
            all_json_history.items(),
            key=lambda item: (item[1].get('liked', False), item[1].get('played', 0)),
            reverse=True
        )

        number_of_songs_to_display = 10
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
