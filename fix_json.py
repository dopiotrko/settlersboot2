import json
import pickle
from files import get_last_filename, get_new_filename
from my_types import Point


class Fix:
    def __init__(self, name):
        self.name = name
        # with open('data/{}/learned.json'.format(name)) as f:
        with open(get_last_filename(name)) as f:
            self.data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        # with open('data/{}/learned_backup.json'.format(self.name), 'w') as f:
        #     json.dump(self.data, f, indent=2)

    def fix_co(self):

        for action in self.data['actions']:
            for general in action['generals']:
                if not general['init']:
                    if 'relative_coordinates' in general:
                        xcr, ycr = self.coordinations['center_ref'].get()
                        xrc, yrc = general['relative_coordinates']
                        general['relative_coordinates'] = [xcr - xrc, ycr - yrc]
        self.save()

    def fix_drag(self):

        for action in self.data['actions']:
            for general in action['generals']:
                if 'drag' in general:
                    xR, yR = self.coordinations['center_ref'].get()
                    xm, ym = general['drag'][0]
                    xd, yd = general['drag'][1]

                    general['drag'] = [(xd - xm) / 2, (yd - ym) / 2]
        self.save()

    def save(self):
        # with open('data/{}/learned.json'.format(self.name), 'w') as f:
        with open(get_new_filename(self.name), 'w') as f:
            json.dump(self.data, f, indent=2)

    def merge(self):
        with open('data/{}/learned_backup.json'.format(self.name)) as f:
            backup = json.load(f)
        for action, action_backup in zip(self.data['actions'], backup['actions']):
            if 'delay' in action:
                action['delay'] = action_backup['delay']
        # self.save()

    def fix_id_no(self):
        # for gen in self.data['generals']:
        #     gen['id'] -= 1
        for action in self.data['actions']:
            action['no'] += 1
            # for general in action['generals']:
            #     general['id'] -= 1
        self.save()

    def rel_cord_del(self):
        for action in self.data['actions']:
            for general in action['generals']:
                if 'relative_coordinates' in general:
                    del general['relative_coordinates']
        # self.save()

    def insert_action(self, to, gen_id=1, type_="move"):
        action_template = {
            "no": to,
            "type": type_,
            "generals": [
                {
                    "id": gen_id,
                    "name": self.data['generals'][gen_id]['name'],
                    "preset": False,
                    "init": False,
                    "army": {
                        "recruit": 0,
                        "bowmen": 0,
                        "militia": 0,
                        "cavalry": 0,
                        "longbowman": 0,
                        "soldier": 0,
                        "crossbowman": 0,
                        "elite_soldier": 0,
                        "cannoneer": 0
                    }
                }
            ],
            "delay": 0
        }

        for action in self.data['actions']:
            if action['no'] >= to:
                action['no'] += 1
        self.data['actions'].insert(to - 1, action_template)
        self.save()


# Fix('horseback').merge()
Fix('CR').insert_action(7, 6, 'unload')
