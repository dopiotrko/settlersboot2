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

    def reverse_fix_co(self):

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


# Fix('DMK').fix_co()
# Fix('wiktor').insert_action(33, 0)
# Fix('CR').insert_action(7, 6, 'unload')
import requests
burl = 'https://ubistatic-a.akamaihd.net/0018/live/GFX_HASHED/building_lib/'
collectibles = [
    "3d22e289f157476f3a79a53c1ce2d16b29064c8a.png",
    "27b0441fe4a8812665b8af61972966d5294a9ecb.png",
    "2283394af62449b6d1012dc0c2a8ddfc2cabd34c.png",
    "c11e14421d3f64ac4cf2f26888deff9f4ad0e964.png",
    "144e19ee3f16e12972695cea95ba2024b9dec3cf.png",
    "c55f730b452e9ac32a2fa2de53f71493712a2db5.png",
    "6d11dcde93afce91bc146f88e622f450201e4fff.png",
    "15e6e9e0530c90735c5cf589c4f7289bfff345ed.png",
    "fd051d9f5c663494141f9c891ae026e9ac0af62b.png",
    "0f6796a0845db6618f98d949a67a0979d03ec7de.png",
    "8c7f90c5f97c733c0975b2db5a6b8e6605549f47.png",
    "2fec40fa97eca571ebb00672a8c73c193f38b71f.png",
    "70dc23e44a76aa0eca1a59cbae657bbd3cfd2b63.png",
    "be974b1d2f2b57bd6d43edfdd08d4768f8e909bb.png",
    "b66acaaa3a29fd7a1ce8ea1654a316ca86127bdf.png",
    "de44eef412ce71fe5dd9275dc67e685ed1f8fd2e.png",
    "b7639e0a05e784364057a1c555ade7863e9e1419.png",
    "c318a870415a5f5eed83785e10e5a886ad8c6cc4.png",
    "dd01c5236d806713229fa7791e310776aa62b965.png",
    "7095574d01338c042aa53c08ef4d4c0c38d51359.png",
    "8d48c788455abfad5e18b8bde4952b9f7ce0162d.png",
    "0848be1ac854a26511a47e0c85a880663a975a08.png",
    "ef295ac38d8f7772a1ed0f382a145ef564c2ec4b.png",
    "e9e1b9782d61146c2795167c4d7c1510681b86a7.png",
    "2640a50bd6148ffe691b5ca386c533701eb14911.png",
    "c0a1d931b960997abdb1b727fa27c9fff26eff58.png",
    "77f9564a4f3a36bae4b5dee6290081f60d9be161.png",
    "d8554de0337f5a4fea7a227154cf572222600846.png",
    "542da7f7b0e2bcc8e8f7348c2502d56f6a3f615b.png",
    "8806f72ac4e322714f1d3f0564c2110443809810.png",
    "3baeb0cffbcc8647681b011bca36347008bf4f78.png",
    "5ddad335cf8a2deb1caad9d742c632942529e4d2.png",
    "5d0f9c3b15d856ea170908830b238d23a7fa066a.png",
    "08beb0ce46efc7a2e67170139060554e72c50cd0.png",
    "41e2ddd8857dbb689db88943e37b810b34e790a5.png",
    "de8e32fd201db2ce4d6ed13568053ed9c2a93891.png",
    "3f24a7c79c7047c1c65e60416276d9f3f8edbd40.png",
    "eef8de2ab600ebe3a866ea4db2e9906c1f1be018.png",
    "57879fa1fcdf116f9cc1b90be758fe422dc1ae00.png",
    "85f7298c6a75698b11b6b5a21750f90d345b1c42.png",
    "e12aae65aabfe05a2220059965d5ecca06edd269.png",
    "1266cc37d5d7c2243ee9c0f2a2ad4ed1da29ae0c.png",
    "2b57691bf0e9fdf52d06df3bdb8f195ec622ca5c.png",
    "39bd270f33fd585365315020ab938866f6ea061e.png",
    "d3fea8ea1bd7568720f782dc6415dab49bb697f5.png",
    "314095c559aafba9844d7d60d586d2570025d875.png",
    "35547500798ad2822b8b1d5d1cf4879e44596ba5.png",
    "470899b868390b6017bb1ec6931cb2d7d83e35b2.png",
    "b1c1400ee024f102417514a5449fd75c63eb95b1.png",
    "3d31ec420b92573da45c321741a0d0081e97c18a.png",
    "d85dd693901cfbd921a319e29da941ef7b4f36ef.png",
    "233979928224b1254b60f63c7eafd96651f9ea6a.png",
    "74b33ba575bb069e8d62e736dbf906dbdc668534.png",
    "41295d3a07b1854f2f4c77204bd926b990a93da3.png",
    "3d22e289f157476f3a79a53c1ce2d16b29064c8a.png",
    "27b0441fe4a8812665b8af61972966d5294a9ecb.png",
    "2283394af62449b6d1012dc0c2a8ddfc2cabd34c.png",
    "c11e14421d3f64ac4cf2f26888deff9f4ad0e964.png",
    "144e19ee3f16e12972695cea95ba2024b9dec3cf.png",
    "c55f730b452e9ac32a2fa2de53f71493712a2db5.png",
    "6d11dcde93afce91bc146f88e622f450201e4fff.png",
    "15e6e9e0530c90735c5cf589c4f7289bfff345ed.png",
    "fd051d9f5c663494141f9c891ae026e9ac0af62b.png",
    "0f6796a0845db6618f98d949a67a0979d03ec7de.png",
    "8c7f90c5f97c733c0975b2db5a6b8e6605549f47.png",
    "2fec40fa97eca571ebb00672a8c73c193f38b71f.png",
    "70dc23e44a76aa0eca1a59cbae657bbd3cfd2b63.png",
    "be974b1d2f2b57bd6d43edfdd08d4768f8e909bb.png",
    "b66acaaa3a29fd7a1ce8ea1654a316ca86127bdf.png",
    "de44eef412ce71fe5dd9275dc67e685ed1f8fd2e.png",
    "b7639e0a05e784364057a1c555ade7863e9e1419.png",
    "c318a870415a5f5eed83785e10e5a886ad8c6cc4.png",
    "d460a625eac8def11ca0ad5d5f157b7f75921633.png",
    "52aeb411b37423259b56ff074e44cb37b10cfd8e.png",
    "7dc1e1f289646ba15aeef107efe7026ebb58e8b1.png",
    "4ea96605998865c72f6f40dc8b28d82d62d16b79.png",
    "7bf4444e950d8526ffa99e6b0bbec2d12661cb46.png",
    "4879d59fc8fa0ce0ba5e87b4c34031f2e16ca5f9.png",
    "9811b58652f7eecd312479c666cb89c3bfe75352.png",
    "c0a1d931b960997abdb1b727fa27c9fff26eff58.png",
    "77f9564a4f3a36bae4b5dee6290081f60d9be161.png",
    "d8554de0337f5a4fea7a227154cf572222600846.png",
    "6ad06e0ac1351d47248d0fa1cf900c3025b24b6e.png",
    "8806f72ac4e322714f1d3f0564c2110443809810.png",
    "47fce2c3efbbb0b51305ef7339bab85f417058aa.png",
    "5ddad335cf8a2deb1caad9d742c632942529e4d2.png",
    "84f8940b6bc60d8eabc2320d42fc73fa57345f9a.png",
    "ef09d55fa6bc5e3ad4e5a1d11394315af11662bf.png",
    "41b8238caac031c265efe08544a21ac4be91f534.png",
    "2b9a56599b90e8f70ee9a948283f6649a0fa97a9.png",
    "c46291560daf1224ea94cb37c9489fffed9008e1.png",
    "df4c7433c1fc6b17eaac94fb2f9f69657fe7e7b3.png",
    "c7986b6a8e08a4da78915bfbb4805e98a3707cb1.png",
    "f31b44c6e175545b648227d5e2de44ea2d38b670.png",
    "bd76cd8196c23aaf73139bc263002cf759afc1ce.png",
    "8257a3e50f6ae19db4aeb2c978949b2d81021a61.png",
    "be3b817311852267b1874a0418c05399a6e45004.png",
    "699019d84356acb04b43b69ca0c75e918ee03647.png",
    "15afc74e10b16aa27ead12729e8fe608fab4cddd.png",
    "a8e12a2d4252ceeae0cc0562a1ffa3524b1fa613.png",
    "0ebc734684a8e9f4bf5184859e05e6e72c0ac7bf.png",
    "68a42d6358860f4f1ce705f4aed3f58e245d7a17.png",
    "4afb3220ff0e36afab7a0fcb6368c1c064885178.png",
    "8c9b74cbb21d4efefdd9ca15152ef9e1d5052501.png",
    "4966a1257774552286f9b5ea1aa12af5388e18f4.png",
    "233979928224b1254b60f63c7eafd96651f9ea6a.png",
    "98ff078c8804608fff67ce5c1f11ee8abeb89633.png",
    "f7890455b2a22f29265b63966cfa22f0dd069906.png",
]
# for collectible in collectibles:
#     r = requests.get(burl + collectible)
#     open('resource/collectables/' + collectible, 'wb').write(r.content)

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
