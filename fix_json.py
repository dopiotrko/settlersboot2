import json
import pickle
import copy
from my import get_last_filename, get_new_filename
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

    def insert_action(self, to, gen_id=1, type_="move", init=False):
        action_template = {
            "no": to,
            "type": type_,
            "generals": [
                {
                    "id": gen_id,
                    "type": self.data['generals'][gen_id]['type'],
                    "preset": False,
                    "init": False,
                    "army": self.data['generals'][gen_id]['army'] if init else
                    {
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

    def copy_action(self, to, from_):
        self.data['actions'].insert(to - 1, copy.copy(self.data['actions'][from_ - 1]))
        self.data['actions'][to - 1]['no'] = to
        for no in range(to, len(self.data['actions'])):
            self.data['actions'][no]['no'] = no + 1
        self.save()

    def move_action(self, to, from_):
        moving = self.data['actions'].pop(from_ - 1)
        self.data['actions'].insert(to - 1, moving)
        for no in range(to - 1 if to < from_ else from_ - 1, len(self.data['actions'])):
            self.data['actions'][no]['no'] = no + 1
        self.save()

    def add_multi_attack(self, to, from_):
        action_template = {
            "no": to,
            "type": "attack",
            "generals": [copy.copy(self.data['actions'][action_no - 1]['generals'][0]) for action_no in from_],
            "delay": 0
        }

        for action in self.data['actions']:
            if action['no'] >= to:
                action['no'] += 1
        self.data['actions'].insert(to - 1, action_template)
        self.save()

    def add_capacity(self):
        capacity = {
            "basic": 200,
            "master": 235,
            "veteran": 250,
            "boris": 195,
            "medic": 200,
            "major": 285,
            "grim": 200
        }
        for gen in self.data['generals']:
            gen['capacity'] = capacity[gen['type']]
        self.save()


# Fix('CR').add_capacity()
# Fix('wiktor').insert_action(33, 0)
# Fix('CR').insert_action(7, 6, 'unload')


class AddMyPyGui:
    @classmethod
    def add(cls, name):
        text = "class {0}:\n" \
               "    def __call__(self, *args, **kwargs):\n" \
               "        print('{0}:', *args, **kwargs)\n" \
               "        pyautogui.{1}(*args, **kwargs)\n" \
               "{1} = {0}()\n\n".format(name.capitalize(), name)

        print(text)
        with open('my_pygui.py', 'a') as f:
            f.write(text)


class LoggingAdd:
    def __init__(self, filename):
        def_line = False
        class_name = None
        with open(filename+'.bcp', 'a') as ff:
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith('class'):
                        import re
                        class_name = re.split('\W+', line)[1]
                    elif line.startswith('    def '):
                        def_line = True
                        import re
                        def_name = re.split('\W+', line)[2]
                    elif def_line:
                        def_line = False
                        if not line.startswith('        loogging'):
                            ff.write("        logging.info('{}:{}:')\n".format(class_name, def_name))
                            # print('\n', file=ff)
                    ff.write(line)


# LoggingAdd('gui.py')

"""
import pytesseract
import cv2 as cv
import time
img = cv.imread('test.png',0)
start = time.time()
scale_percent = 400 # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
# resize image
resized = cv.resize(img, dim, interpolation=cv.INTER_LINEAR)

# cv.imwrite('testres.png', resized)

_, thresh2 = cv.threshold(resized, 127, 255, cv.THRESH_BINARY_INV)

# cv.imwrite('group_test.png', thresh2)

# test1 = cv.imread('test1.png',0)

custom_config = r'-c tessedit_char_whitelist="1234567890/ " --psm 6'
# custom_config = r'--oem 3 --psm 6 outputbase digits'
# print(pytesseract.image_to_string(thresh2, config=custom_config))
d = pytesseract.image_to_data(thresh2, output_type=pytesseract.Output.DICT, config=custom_config)
for key, items in d.items():
    print('\n{:>10}'.format(key), end='')
    for item in items:
        print('{:>10}'.format(item), end='')

# custom_config = r'-c tessedit_char_whitelist="/ " --psm 6'
# d = pytesseract.image_to_data(test1, output_type=pytesseract.Output.DICT, config=custom_config)
# for key, items in d.items():
#     print('\n{:>10}'.format(key), end='')
#     for item in items:
#         print('{:>10}'.format(item), end='')

date_pattern = '/'
have = dict((key, []) for key in d.keys())
# to_have = dict((key, []) for key in d.keys())
n_boxes = len(d['text'])
for i in range(n_boxes):
    if int(d['level'][i]) == 5:
        for key in d:
            have[key].append(d[key][i])

print('')
for i in range(len(have['text'])):
    if i % 2:
        (x, y, w, h) = (have['left'][i], have['top'][i], have['width'][i], have['height'][i])
        roi = thresh2[y:y+h, x+20:x+w]
        # cv.imwrite('roi{}.png'.format(i), roi)
        custom_config = r'--oem 3 --psm 7 outputbase digits'
        print(pytesseract.image_to_string(roi, config=custom_config))
        # test1 = cv.rectangle(test1, (x+20, y), (x + w, y + h), (0, 255, 0), 2)

print('')
print(list(no for i, no in enumerate(have['text']) if not i % 2))
print(time.time()-start)
print('')
# print(have)
# cv.imwrite('test2.png', test1)
# cv.imshow('test1', test1)
# cv.waitKey(0)
"""
