import json
import os
from datetime import datetime

from lib.log import Logger


class HistoryManager:

    def __init__(self, max_local_history_size=10):
        self.history_folder = "history"
        self.history_file = "history.json"
        self.history = {}
        self.max_local_history_size = max_local_history_size
        self.log = Logger.get_log(self.__class__.__name__)

    def add_to_history(self, signature_key, musical_key=None):

        if len(self.history) == self.max_local_history_size:
            self.save_history()

        if signature_key in self.history:
            return

        base_history_object = {
            'signature_key': signature_key,
            'key': musical_key,
            'played': 0,
            'liked': False,
            'disliked': False,
            'tags': [],
            'lastPlayed': None
        }

        self.history[signature_key] = base_history_object

    def like(self, signature_key):
        if signature_key not in self.history:
            self.add_to_history(signature_key)
        self.history[signature_key]['liked'] = True
        self.history[signature_key]['disliked'] = False

    def dislike(self, signature_key):
        if signature_key not in self.history:
            self.add_to_history(signature_key)
        self.history[signature_key]['disliked'] = True
        self.history[signature_key]['liked'] = False

    def incr_played(self, signature_key):
        if signature_key not in self.history:
            self.add_to_history(signature_key)
        self.history[signature_key]['played'] += 1
        self.history[signature_key]['lastPlayed'] = str(datetime.now())

    def add_tag(self, signature_key, tag):
        if signature_key not in self.history:
            self.add_to_history(signature_key)
        self.history[signature_key]['tags'].append(tag)

    def load_history(self, file_name=None):
        if file_name is None:
            file_name = self.history_file

        history_file_path = os.path.join(self.history_folder, file_name)

        if not os.path.exists(history_file_path):
            return None

        return json.load(open(history_file_path, 'r'))

    def save_history(self, file_name=None):
        if file_name is None:
            file_name = self.history_file

        history_file_path = os.path.join(self.history_folder, file_name)

        historical_data = None
        if os.path.exists(history_file_path):
            with open(history_file_path, 'r') as file:
                historical_data = json.load(file)

        if not historical_data:
            historical_data = {}

        for signature_key in self.history:
            # data in current history
            data = self.history[signature_key]

            if signature_key in historical_data:
                # song has been played before
                # so update the loaded data in historical_data
                historical_item_data = historical_data[signature_key]

                historical_item_data['played'] += data['played']
                historical_item_data['liked'] |= data['liked']
                if data['disliked']:
                    historical_item_data['disliked'] = data['disliked']
                    historical_item_data['liked'] = False

                historical_item_data['tags'] = historical_item_data['tags'] + data['tags']

                if data['lastPlayed']:
                    historical_item_data['lastPlayer'] = data['lastPlayed']

                historical_data[signature_key] = historical_item_data
            else:
                historical_data[signature_key] = data

        with open(history_file_path, 'w') as file:
            json.dump(historical_data, file)

        self.log.info("Dumped to history file successfully")
        self.history = {}
