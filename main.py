# sudo apt-get install scrot
# sudo apt-get install python3-tk python3-dev
# pip install opencv-contrib-python # in your venv
# pip install pyautogui
# pip install pynput
"""
pytesseract INSTALLATION
Prerequisites:

Python-tesseract requires Python 2.7 or Python 3.5+

You will need the Python Imaging Library (PIL) (or the Pillow fork). Under Debian/Ubuntu,
this is the package python-imaging or python3-imaging.

Install Google Tesseract OCR (additional info how to install the engine on Linux, Mac OSX and Windows).
You must be able to invoke the tesseract command as tesseract.
If this isn’t the case, for example because tesseract isn’t in your PATH,
you will have to change the “tesseract_cmd” variable pytesseract.pytesseract.tesseract_cmd.
Under Debian/Ubuntu you can use the package tesseract-ocr.
For Mac OS users. please install homebrew package tesseract.

Note: Make sure that you also have installed tessconfigs and configs from tesseract-ocr/tessconfigs or via the
OS package manager.

Installing via pip:
Check the pytesseract package page for more information.
$ (env)> pip install pytesseract
"""

import json
import pickle
import time
import my_pygui
import logging
import my
import listener
import ocr
import os
from my_types import Point, Mode
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO)
STAROPEN = False


class Adventure:
    def __init__(self, name):
        logging.info('Init Adventure:')
        self.name = name
        with open(my.get_last_filename(name)) as f:
            self.data = json.load(f)
        # with open('data/{}/learned.json'.format(name)) as f:
        #     self.data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

    def init_locate_generals(self, start):
        logging.info('init_locate_generals:')
        time.sleep(.5)
        if start == 0 or not os.path.exists('data/{}/generals_loc.dat'.format(self.name)):
            generals = dict()
            my_pygui.click(self.coordinations['star'].get())
            my_pygui.click(self.coordinations['specialists'].get())
            for general in self.data['generals']:
                print(general)
                if general['type'] in generals:
                    generals[general['type']].append(general['id'])
                else:
                    generals[general['type']] = [general['id']]
            generals_loc = 100 * [None]
            for general_type, ids in generals.items():
                star_window_cor = self.coordinations['specialists'] - Point(137, 400)
                locations = list(my_pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                                            region=(star_window_cor.x, star_window_cor.y, 600, 400),
                                                            confidence=0.97))
                locations.extend(my_pygui.locateAllOnScreen('resource/{}_.png'.format(general_type),
                                                            region=(star_window_cor.x, star_window_cor.y, 600, 400),
                                                            confidence=0.97))
                # TODO necessary if part of army sent back. Temporary solution.
                if not locations:
                    continue
                locations.sort(key=lambda i: i.y)
                y_standardized = locations[0].y
                for loc in locations:
                    if abs(y_standardized - loc.y) < 10:
                        loc.y = y_standardized
                    else:
                        y_standardized = loc.y
                locations.sort(key=lambda i: i.y*10000+i.x)
                for id_ in ids:
                    generals_loc[id_] = locations.pop(0)
            while True:
                try:
                    generals_loc.remove(None)
                except ValueError:
                    break
            my_pygui.click(self.coordinations['star'].get())
            with open('data/{}/generals_loc.dat'.format(self.name), 'wb') as generals_loc_file:
                pickle.dump(generals_loc, generals_loc_file)
        else:
            with open('data/{}/generals_loc.dat'.format(self.name), 'rb') as generals_loc_file:
                generals_loc = pickle.load(generals_loc_file)
        return generals_loc

    def group_generals_by_types(self, first, last):
        logging.info('group_generals_by_types')
        generals = dict()
        # pygui.click(self.coordinations['star'].get())
        # pygui.click(self.coordinations['specialists'].get())
        for general in self.data['generals']:
            if not(first <= general['id'] <= last):
                continue
            if general['type'] in generals:
                generals[general['type']].append(general)
            else:
                generals[general['type']] = [general]
        return generals

    def start_adventure(self, delay=0):
        logging.info('start_adventure')

        my.wait(delay, 'Starting adventure')

        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['adventures'].get())

        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = my_pygui.locateOnScreen('data/{}/start_adv.png'.format(self.name),
                                      region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                      confidence=0.85)
        if loc is None:
            raise Exception('No adventures {} found.'.format(self.name))
        else:
            my_pygui.click(loc.get())
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())
        loc = my_pygui.locateOnScreen('resource/confirm.png'.format(self.name), confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())

    def set_army(self, general_loc, general):
        logging.info('set_army')
        count = 0
        army = general['army']
        while True:
            logging.info('Setting army, try {}'.format(count+1))
            my_pygui.click(self.coordinations['unload'].get())
            for units, quantity in army.items():
                if quantity != 0:
                    init_x, y = self.coordinations[units].get()
                    for x in range(init_x, init_x-50, -24):
                        if not my_pygui.pixelMatchesColor(x, y, (131, 102, 65), tolerance=10):
                            loc = x, y-7
                            break
                    else:
                        raise Exception('text field not found')
                    my_pygui.click(loc)
                    my_pygui.write('{}'.format(quantity))
            my_pygui.click(self.coordinations['confirm_army'].get())
            time.sleep(4)
            """verify"""
            x_t, y_t = self.coordinations['move'].get()
            finded, re_selected = False, False
            while not finded:
                for i in range(3):
                    finded = my_pygui.locateOnScreen('resource/transfer.png',
                                                     region=(x_t-25, y_t-25, 50, 50),
                                                     confidence=0.97)
                    if finded:
                        logging.info('General ready = transfer button active')
                        break
                    else:
                        logging.warning('General not ready yet. Trying again after 3 sec')
                        my.wait(3, 'Trying again')
                else:
                    """re selecting only once"""
                    if not re_selected:
                        logging.warning('General not ready after 3 tryes. Re selecting')
                        self.select_general_by_loc(general_loc, general['type'], wait_til_active=False)
                        re_selected = True
                    else:
                        logging.error('General not ready after re select. Abort')
                        raise Exception('General not ready after re select.')
            x, y = self.coordinations['army_sum'].get()
            army_sum_screen = my_pygui.screenshot(region=(x, y, 314, 14))
            if ocr.assigned_unit_sum(army_sum_screen) == sum(army.values()):
                break
            else:
                """try again"""
                logging.warning('Try {} failed'.format(count + 1))
                count += 1
                if count >= 3:
                    raise Exception('Could not set army in 3 tryes')

    def select_general_by_loc(self, loc, general_type, wait_til_active=True):
        logging.info('select_general_by_loc')

        x, y = self.coordinations['star'].get()
        my_pygui.moveTo(x, y, .2)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        if wait_til_active:
            while True:
                finded = my_pygui.locateOnScreen('resource/{}.png'.format(general_type),
                                                 region=(loc.x-30, loc.y-30, 60, 60),
                                                 confidence=0.97)
                if finded:
                    break
                else:
                    logging.warning('no active general of type {} found in this location. Trying again after 3 sec')
                    my.wait(3, 'Trying again')
        my_pygui.click(loc.get())

    def get_generals_by_type(self, general_type, general_name=None):
        logging.info('get_generals_by_type')

        x, y = self.coordinations['star'].get()
        my_pygui.moveTo(x, y, .2)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        general = general_name or general_type
        my_pygui.write(general)
        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        locations = my_pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                               region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                               confidence=0.97)
        return locations

    def send_generals_by_type(self, general_type, list_of_dicts_with_generals_of_that_type, general_name=None):
        logging.info('send_generals_by_type')

        locations_of_gens_of_that_type = self.get_generals_by_type(general_type, general_name)
        generals_of_type = list(zip(list_of_dicts_with_generals_of_that_type, locations_of_gens_of_that_type))
        generals_of_type.reverse()
        for item_no, (gen_to_send, available_gen_loc) in enumerate(generals_of_type):
            my_pygui.click(available_gen_loc.get())
            self.set_army(available_gen_loc, gen_to_send)
            my_pygui.click(self.coordinations['send'].get())
            my_pygui.click(self.coordinations['send_confirm'].get())
            time.sleep(2)
            if item_no < len(generals_of_type)-1:
                my_pygui.click(self.coordinations['star'].get())
                my_pygui.click(self.coordinations['specialists'].get())

    def sum_armies(self, first, last):
        logging.info('sum_generals_army')
        army = dict()
        for general in self.data['generals']:
            if not(first <= general['id'] <= last):
                continue
            army = {key: army.get(key, 0) + val for key, val in general['army'].items()}
        return army

    def check_if_army_available(self, army):
        # TODO temporally disable this function
        return
        logging.info('check_if_army_available')
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.write('genera')
        my_pygui.click(self.coordinations['first_general'].get())
        time.sleep(.5)
        for key, val in army.items():
            if val:
                logging.info('Checking available {}'.format(key))
                x, y = self.coordinations[key].get()
                screen = my_pygui.screenshot(region=(x-43, y-13, 82, 13))
                if ocr.available_unit(screen) < val:
                    raise Exception('Not enough {}'.format(key))
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.press('del')
        my_pygui.click(self.coordinations['star'].get())

    def send_to_adventure(self, delay=0, first=0, last=100):
        logging.info('send_to_adventure')

        my.wait(delay, 'Sending to adventure')
        army = self.sum_armies(first, last)
        print(army)
        self.check_if_army_available(army)
        for g_type, generals_of_type in self.group_generals_by_types(first, last).items():
            unnamed_generals_of_type = []
            for general in generals_of_type:
                """sending named generals first"""
                if 'name' in general:
                    self.send_generals_by_type(g_type, (general,), general['name'])
                else:
                    unnamed_generals_of_type.append(general)
            """sending rest of generals"""
            if unnamed_generals_of_type:
                self.send_generals_by_type(g_type, unnamed_generals_of_type)
        """reset star window to default"""
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.press('del')
        my_pygui.click(self.coordinations['star'].get())

    def go_to_adventure(self, delay=0):
        logging.info('go_to_adventure')

        my.wait(delay, 'Going to adventure')
        loc = my_pygui.locateOnScreen('data/{}/goto_adv.png'.format(self.name), confidence=0.85)
        if loc is None:
            raise Exception('No active adventure {} found on the screen.'.format(self.name))
        else:
            x, y = loc.get()
            my_pygui.click(x, y)
            my_pygui.click(x, y + 15)

    def make_adventure(self, delay=0, start=0, stop=1000, mode=Mode.play):
        logging.info('make_adventure')
        assert(isinstance(mode, Mode))
        my.wait(delay, 'Making adventure')
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star'] - Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.press('-', presses=2)
        generals_loc = self.init_locate_generals(start)
        get_click = listener.GetClick()
        for action in self.data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            if not start == action['no']:
                if mode == Mode.play:
                    my.wait(action['delay'], 'Next action ({})in'.format(action['no']))
                elif mode == Mode.teach_delay:
                    t_start = time.time()
                    text = 'Click OK when you want to do {1} ({0}) with generals:\n'.format(action['no'],
                                                                                            action['type'])
                    for gen in action['generals']:
                        text += '{:3} - {:10}\n'.format(gen['id'], gen['type'])
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    action['delay'] = int(time.time() - t_start)
                elif mode == Mode.teach_co:
                    text = 'Click OK when You want to make Your action ({}) no {}' \
                        .format(action['type'], action['no'])
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')

            print(action['no'], time.asctime(time.localtime(time.time())))
            for i, general in enumerate(action['generals']):
                general_loc = generals_loc[general['id']]
                t_0 = time.time()
                if 'retreat' in general:
                    my.wait(5, 'Re selecting general')
                    self.select_general_by_loc(general_loc,  general['type'], wait_til_active=False)
                    if mode == Mode.play or mode == Mode.teach_co:
                        my.wait(general['delay'], 'General retreat')
                        my_pygui.click(self.coordinations['retreat'].get())
                    elif mode == Mode.teach_delay:
                        text = 'Click when You want to retreat general'
                        my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                        my_pygui.click(self.coordinations['retreat'].get())
                        general['delay'] = int(time.time() - t_0)
                    continue
                else:
                    """only first general is verified if is active (assume rest is - to save time)"""
                    wait_til_active = i == 0
                    self.select_general_by_loc(general_loc, general['type'], wait_til_active=wait_til_active)
                if not general['preset']:
                    self.set_army(general_loc, general)
                    if action['type'] in ('unload', 'load'):
                        continue
                if action['type'] in 'attack':
                    my_pygui.click(self.coordinations['attack'].get())
                    text = 'Make Your attack no {}'.format(action['no'])
                elif action['type'] in 'move':
                    my_pygui.click(self.coordinations['move'].get())
                    text = 'Move your army'
                else:
                    raise Exception('Unexpected action type ')
                if mode == Mode.play or mode == Mode.teach_delay:
                    if 'drag' in general:
                        my_pygui.moveTo((self.coordinations['center_ref'] - Point.from_list(general['drag'])).get())
                        my_pygui.dragTo((self.coordinations['center_ref'] + Point.from_list(general['drag'])).get())
                elif mode == Mode.teach_co:
                    answer = my_pygui.confirm(text='Do You see the target?\n'
                                                   ' If not chose \'Drag first\' and drag island to see the target',
                                              title='Teaching Adventure {}'.format(self.name),
                                              buttons=['I see it. Proceed', 'Drag First'])
                    if answer == 'Drag First':
                        general['drag'] = get_click.get('DRAG')
                        xm, ym = general['drag'][0]
                        xd, yd = general['drag'][1]
                        general['drag'] = [(xd - xm) / 2, (yd - ym) / 2]
                if general['init'] is True:
                    my_pygui.moveTo((self.coordinations['book'] + Point(100, 0)).get())
                    finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
                    if not finded:
                        raise Exception('data/{}/loc_reference.png not found on screen'.format(self.name))
                    if mode == Mode.teach_co:
                        my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                        general['relative_coordinates'] = (get_click.get('DOUBLE') - finded).get()
                    elif mode == Mode.play or mode == Mode.teach_delay:
                        target = Point.from_list(general['relative_coordinates']) + finded
                        if 'delay' in general:
                            if mode == Mode.play:
                                my.wait(general['delay'], 'Next general attacks')
                            elif mode == Mode.teach_delay:
                                my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                                general['delay'] = int(time.time() - t_0)
                        my_pygui.click(target.get(), clicks=2, interval=0.25)
                else:
                    if mode == Mode.play or mode == Mode.teach_delay:
                        target = self.coordinations['center_ref'] - Point.from_list(general['relative_coordinates'])
                        my_pygui.moveTo(target.get())
                        if 'delay' in general:
                            if mode == Mode.play:
                                my.wait(general['delay'], 'Next general attacks')
                            elif mode == Mode.teach_delay:
                                my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                                general['delay'] = int(time.time() - t_0)
                        my_pygui.click(target.get(), clicks=2, interval=0.25)
                    elif mode == Mode.teach_co:
                        my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                        xcr, ycr = self.coordinations['center_ref'].get()
                        xrc, yrc = get_click.get('DOUBLE').get()
                        general['relative_coordinates'] = [xcr - xrc, ycr - yrc]

            if mode == Mode.teach_delay or mode == Mode.teach_co:
                with open(my.get_new_filename(self.name), 'w') as f:
                    json.dump(self.data, f, indent=2)

    def end_adventure_(self, delay=0):
        logging.info('end_adventure')

        my.wait(delay, 'Ending adventure')
        my_pygui.click(self.coordinations['book'].get())
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())
        loc = my_pygui.locateOnScreen('resource/confirm.png', confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())
        time.sleep(20)
        loc = my_pygui.locateOnScreen('data/{}/return_ref.png'.format(self.name), confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click((loc + Point(160, 234)).get())

    def end_adventure(self, delay=0, mode=Mode.teach_co):
        logging.info('end_adventure')

        my.wait(delay, 'Ending adventure')
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['first_general'].get())
        my_pygui.click(self.coordinations['close_general'].get())
        finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
        if not finded:
            raise Exception('data/{}/loc_reference.png not found on screen'.format(self.name))
        end_adventure_co = []
        get_click = listener.GetClick()
        if mode == Mode.teach_co:
            while True:
                t_0 = time.time()
                coord = get_click.get('DOWN')
                if coord == 'right':
                    break
                end_adventure_co.append({"co": (coord - finded).get(), "delay": time.time() - t_0})
            with open('data/{}/end_adv_co.json'.format(self.name), 'w') as f:
                json.dump(end_adventure_co, f, indent=2)
        elif mode == Mode.play:
            with open('data/{}/end_adv_co.json'.format(self.name), 'r') as f:
                end_adventure_co = json.load(f)
            for click in end_adventure_co:
                target = Point.from_list(click['co']) + finded
                if mode == Mode.play:
                    my.wait(click['delay'], 'Next click')
                my_pygui.moveTo(target.get())
                my_pygui.click(target.get(), clicks=1, interval=0.25)


# Configure().run()
adventure = 'traitors'
# adventure = 'WW'
TN = Adventure(adventure)
# Adventure('Home').make_adventure(delay=6*60)
# TN.make_adventure(delay=3, start=2, stop=111, mode=Mode.play)
# TN.end_adventure(100, Mode.play)
# Adventure('Home').make_adventure(delay=8*60)
# for i in range(20):
#     TN.start_adventure(delay=3)
#     TN.send_to_adventure(first=0, last=111)
#     TN.go_to_adventure(7*60)
#     TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
#     TN.end_adventure(100, Mode.play)
#     Adventure('Home').make_adventure(delay=8*60)

# TN.start_adventure(delay=3)
# TN.send_to_adventure(first=0, last=11)
# TN.send_to_adventure(first=4, last=4)
# TN.go_to_adventure(7)
# TN.make_adventure(delay=3, start=0, stop=23, mode=Mode.play)
# TN.end_adventure(1, Mode.play)

# Adventure('Home').make_adventure(delay=6*60)
# TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
# TN.end_adventure(100, Mode.play)
# Adventure('Home').make_adventure(delay=5*60)
# Adventure('lg_9').send_to_adventure(3)
# Adventure('lg_9').make_adventure(3, mode=Mode.teach_delay)
Adventure('spj').make_adventure(3)
# Adventure('oblezenie').send_to_adventure(3)
Adventure('oblezenie').make_adventure(3000)
TN = Adventure('traitors')
# TN.start_adventure(delay=3)
# TN.send_to_adventure(20, first=0, last=1)
# Adventure('a_WW').make_adventure(delay=8*60)
# TN.send_to_adventure(2*60, first=2, last=11)
# TN.go_to_adventure(7 * 60)
TN.make_adventure(delay=3, start=1, stop=137, mode=Mode.play)
TN.end_adventure(120, Mode.play)
Adventure('a_WW').make_adventure(delay=8*60)
for i in range(20):
    TN = Adventure('WW')
    TN.start_adventure(delay=30)
    TN.send_to_adventure(first=0, last=111)
    TN.go_to_adventure(7*60)
    TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
    TN.end_adventure(100, Mode.play)
    TN = Adventure('traitors')
    TN.start_adventure(delay=80)
    TN.send_to_adventure(20, first=0, last=1)
    Adventure('a_WW').make_adventure(delay=6*60)
    TN.send_to_adventure(first=2, last=11)
    TN.go_to_adventure(7 * 60)
    TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
    TN.end_adventure(120, Mode.play)
    Adventure('a_WW').make_adventure(delay=8*60)
