import json
import pickle
from my_types import Point

class Fix:
    def __init__(self, name):
        self.name = name
        with open('data/{}/learned.json'.format(name)) as f:
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
        with open('data/{}/learned.json'.format(self.name), 'w') as f:
            json.dump(self.data, f, indent=2)


Fix('horseback').fix_co()
