import json
import os


class HistoryManager:

    def __init__(self):
        self.history_folder = "history"
        self.history_file = "history.json"
        self.history = {}

    def add_to_history(self, signature_key, musical_key=None):
        base_history_object = {
            'signature_key': signature_key,
            'key': musical_key,
            'played': 0,
            'liked': False,
            'disliked': False,
            'tags': []
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

                historical_data[signature_key] = historical_item_data
            else:
                historical_data[signature_key] = data

        with open(history_file_path, 'w') as file:
            json.dump(historical_data, file)

        print("dumped to history file successfully")
        self.history = {}
