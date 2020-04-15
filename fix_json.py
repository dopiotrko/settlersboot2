import json


class Fix:
    def __init__(self, name):
        with open('data/{}/learned.json'.format(name)) as f:
            self.data = json.load(f)

    def fix(self):
        pass

