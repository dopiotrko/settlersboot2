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
log = logging.getLogger(__name__)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO)
STAROPEN = False


class Adventure:
    def __init__(self, name):
        log.info('Init Adventure:')
        self.name = name
        with open(my.get_last_filename(name)) as f:
            self.data = json.load(f)
        # with open('data/{}/learned.json'.format(name)) as f:
        #     self.data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        self.generals_loc = None
        self.focused = None

    def init_locate_generals(self, start=0):
        log.info('init_locate_generals:')
        time.sleep(.5)
        if start == 0 or not os.path.exists('data/{}/generals_loc.dat'.format(self.name)):
            generals = dict()
            self.open_star()
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
                locations.sort(key=lambda i: i.y * 10000 + i.x)
                for id_ in ids:
                    generals_loc[id_] = locations.pop(0)
            while True:
                try:
                    generals_loc.remove(None)
                except ValueError:
                    break
            my_pygui.click(self.coordinations['star_close'].get())
            with open('data/{}/generals_loc.dat'.format(self.name), 'wb') as generals_loc_file:
                pickle.dump(generals_loc, generals_loc_file)
        else:
            with open('data/{}/generals_loc.dat'.format(self.name), 'rb') as generals_loc_file:
                generals_loc = pickle.load(generals_loc_file)
        return generals_loc

    def group_generals_by_types(self, first, last):
        log.info('group_generals_by_types')
        generals = dict()
        # pygui.click(self.coordinations['star'].get())
        # pygui.click(self.coordinations['specialists'].get())
        for general in self.data['generals']:
            if not (first <= general['id'] <= last):
                continue
            if general['type'] in generals:
                generals[general['type']].append(general)
            else:
                generals[general['type']] = [general]
        return generals

    def open_star(self, verify=True):
        log.info('open_star')
        my_pygui.click(self.coordinations['star'].get())
        try_count = 0
        while verify:
            log.info('verify if star is open')
            star_close = self.coordinations['star_close']
            time.sleep(.5)
            loc = my_pygui.locateOnScreen('resource/star_verify.png'.format(self.name),
                                          region=(star_close.x - 20, star_close.y, 40, 45),
                                          confidence=0.85)
            if loc:
                log.info('star open verification succeed')
                break
            else:
                log.info('star open verification false - trying again')
                my.wait(try_count, 'star open verification false - trying again')
                my_pygui.click(self.coordinations['star'].get())
                if try_count < 10:
                    try_count += 1
                else:
                    raise Exception('star open verification failed in 10 tryes')

    def start_adventure(self, adv_name, delay=0):
        log.info('start_adventure {}'.format(adv_name))

        my.wait(delay, 'Starting adventure')

        self.open_star()
        my_pygui.click(self.coordinations['adventures'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.write(adv_name)
        my.wait(2, 'Adv search')
        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = my_pygui.locateOnScreen('resource/is_adv.png'.format(self.name),
                                      region=(star_window_corner.x, star_window_corner.y, 95, 73),
                                      confidence=0.85)
        if loc is None:
            raise Exception('No adventures {} found.'.format(self.name))
        else:
            my_pygui.click(self.coordinations['first_general'].get())
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
        self.open_star()
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.hotkey('del')

    def set_army(self, general_loc, general):
        log.info('set_army')
        count = 0
        army = general['army']
        time.sleep(2)
        loc = my_pygui.locateOnScreen('resource/army.png',
                                      region=self.coordinations['first_army_region'],
                                      confidence=.95,
                                      center=False)
        elite = general.get('elite', False)
        if (loc and elite) or (not loc and not elite):
            my_pygui.click(self.coordinations['elite'].get())
            time.sleep(3)
        while True:
            log.info('Setting army, try {}'.format(count + 1))
            my_pygui.click(self.coordinations['unload'].get())
            for units, quantity in army.items():
                if quantity != 0:
                    init_x, y = self.coordinations[units].get()
                    for x in range(init_x, init_x - 50, -24):
                        if not my_pygui.pixelMatchesColor(x, y, (131, 102, 65), tolerance=10):
                            loc = x, y - 7
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
                                                     region=(x_t - 30, y_t - 165, 60, 200),
                                                     confidence=0.97)
                    if finded:
                        log.info('General ready = transfer button active')
                        break
                    else:
                        log.warning('General not ready yet. Trying again after 3 sec')
                        my.wait(3, 'Trying again')
                else:
                    """re selecting only once"""
                    if not re_selected:
                        log.warning('General not ready after 3 tryes. Re selecting')
                        self.select_general_by_loc(general_loc, general['type'], verify=False)
                        re_selected = True
                    else:
                        log.error('General not ready after re select. Abort')
                        raise Exception('General not ready after re select.')
            x, y = self.coordinations['army_sum'].get()
            army_sum_screen = my_pygui.screenshot(region=(x, y, 314, 14))
            if ocr.assigned_unit_sum(army_sum_screen) == sum(army.values()):
                break
            else:
                """try again"""
                log.warning('Try {} failed'.format(count + 1))
                count += 1
                if count >= 3:
                    raise Exception('Could not set army in 3 tryes')

    def select_general_by_loc(self, loc, general_type, verify=True, recursion=0):
        log.info('select_general_by_loc')
        """selecting general by loc from star, 
        return True if selected and on map, 
        return False if selected but retreated,
        raise Exception if selection failed"""
        x, y = self.coordinations['star'].get()
        my_pygui.moveTo(x, y, .2)
        self.open_star(verify)
        my_pygui.click(self.coordinations['specialists'].get())
        if verify:
            log.info('verify if general is active')
            t0 = time.time()
            while True:
                if self.verify_if_general_active(loc, general_type):
                    log.info('active general selected after {} s.'.format(time.time()-t0))
                    break
        my_pygui.click(loc.get())
        # verify if general opened
        x_t, y_t = self.coordinations['move'].get()
        time.sleep(.5)
        finded = my_pygui.locateOnScreen('resource/transfer.png',
                                         region=(x_t - 30, y_t - 165, 60, 200),
                                         confidence=0.97)
        if finded:
            return True
        else:
            x_t, y_t = self.coordinations['star'].get()
            finded = my_pygui.locateOnScreen('resource/star_cancel.png',
                                             region=(x_t - 95, y_t - 80, 190, 120),
                                             confidence=0.97)
            if finded:
                return False
            else:
                recursion += 1
                if recursion < 5:
                    msg = 'general selection failed in try {}, trying again'.format(recursion)
                    log.warning(msg)
                    my.wait(recursion, msg)
                else:
                    msg = 'general selection failed in 5 tryes '
                    log.error(msg)
                    raise Exception(msg)
                return self.select_general_by_loc(loc, general_type, verify, recursion=recursion)

    @staticmethod
    def verify_if_general_active(loc, general_type):
        finded = my_pygui.locateOnScreen('resource/{}.png'.format(general_type),
                                         region=(loc.x - 30, loc.y - 30, 60, 60),
                                         confidence=0.97)
        if finded:
            return True
        else:
            log.warning('no active general of type {} found in this location. Trying again after 3 sec')
            time.sleep(3)
            return False

    def get_generals_by_type(self, general_type, general_name=None):
        log.info('get_generals_by_type')

        x, y = self.coordinations['star'].get()
        my_pygui.moveTo(x, y, .2)
        self.open_star()
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
        log.info('send_generals_by_type')

        locations_of_gens_of_that_type = self.get_generals_by_type(general_type, general_name)
        generals_of_type = list(zip(list_of_dicts_with_generals_of_that_type, locations_of_gens_of_that_type))
        generals_of_type.reverse()
        if not generals_of_type:
            log.error('No general {} [{}]'.format(general_type, general_name))
            raise Exception('No general {} [{}]'.format(general_type, general_name))
        for item_no, (gen_to_send, available_gen_loc) in enumerate(generals_of_type):
            my_pygui.click(available_gen_loc.get())
            self.set_army(available_gen_loc, gen_to_send)
            if general_type == 'kwatermistrz':
                send_co = self.coordinations['send'] - Point(0, 127)
            else:
                send_co = self.coordinations['send']
            my_pygui.click(send_co.get())
            my_pygui.click(self.coordinations['send_confirm'].get())
            time.sleep(2)
            if item_no < len(generals_of_type) - 1:
                self.open_star()
                my_pygui.click(self.coordinations['specialists'].get())

    def sum_armies(self, first, last):
        log.info('sum_generals_army')
        army_basic, army_elite = dict(), dict()
        for general in self.data['generals']:
            if not (first <= general['id'] <= last):
                continue
            if 'elite' in general and general['elite']:
                army_elite = {key: army_elite.get(key, 0) + val for key, val in general['army'].items()}
            else:
                army_basic = {key: army_basic.get(key, 0) + val for key, val in general['army'].items()}
        return dict(army_basic, **army_elite)

    def retrench_all(self, delay):
        log.info('retrench_all')
        my.wait(delay, "delay")
        if not self.generals_loc:
            self.generals_loc = self.init_locate_generals()
        for general in self.data['generals']:
            general_loc = self.generals_loc[general['id']]
            # my.wait(5, 'Re selecting general')
            on_map = self.select_general_by_loc(general_loc, general['type'], verify=False)
            if on_map:
                loc = my_pygui.locateOnScreen('resource/retrench.png'.format(self.name), confidence=0.85)
                my_pygui.click(loc.get())
                loc = my_pygui.locateOnScreen('resource/confirm.png'.format(self.name), confidence=0.9)
                my_pygui.click(loc.get())

    def check_if_army_available(self, army):
        # TODO temporally disable this function
        return
        log.info('check_if_army_available')
        self.open_star()
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.write('genera')
        my_pygui.click(self.coordinations['first_general'].get())
        time.sleep(.5)
        for key, val in army.items():
            if val:
                log.info('Checking available {}'.format(key))
                x, y = self.coordinations[key].get()
                screen = my_pygui.screenshot(region=(x - 43, y - 13, 82, 13))
                if ocr.available_unit(screen) < val:
                    raise Exception('Not enough {}'.format(key))
        self.open_star()
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.press('del')
        my_pygui.click(self.coordinations['star_close'].get())

    def send_to_adventure(self, delay=0, first=0, last=100):
        log.info('send_to_adventure')

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
        self.open_star()
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.press('del')
        my_pygui.click(self.coordinations['star_close'].get())

    def go_to_adventure(self, delay=0):
        log.info('go_to_adventure')

        my.wait(delay, 'Going to adventure')
        loc = my_pygui.locateOnScreen('data/{}/goto_adv.png'.format(self.name), confidence=0.85)
        if loc is None:
            raise Exception('No active adventure {} found on the screen.'.format(self.name))
        else:
            x, y = loc.get()
            my_pygui.click(x, y)
            my_pygui.click(x, y + 15)

    def make_adventure(self, delay=0, start=0, stop=1000, mode=Mode.play):
        log.info('make_adventure')
        assert (isinstance(mode, Mode))
        my.wait(delay, 'Making adventure')
        if not self.generals_loc:
            self.generals_loc = self.init_locate_generals(start)
        for action in self.data['actions']:
            if not (start <= action['no'] <= stop):
                continue
            self.make_action(action, mode, start)

    def focus(self):
        log.info('focus')
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star'] - Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.press('-', presses=2)
        self.focused = True

    def make_action(self, action, mode, start):
        log.info('make_action')
        if not self.focused:
            self.focus()
        get_click = listener.GetClick()
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

        if len(action['generals']) > 1:
            self.verify_if_generals_active(action)

        for i, general in enumerate(action['generals']):
            general_loc = self.generals_loc[general['id']]
            t_0 = time.time()
            if 'retreat' in general:
                my.wait(5, 'Re selecting general')
                on_map = self.select_general_by_loc(general_loc, general['type'], verify=False)
                if not on_map:
                    raise Exception('general must be on map to retreat')
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
                """only for first general - verify if star is open, and general is active 
                (assume rest is - to save time)"""
                verify = i == 0
                on_map = self.select_general_by_loc(general_loc, general['type'], verify=verify)
            if on_map:
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
            else:
                if action['type'] not in 'move':
                    raise Exception("for generals not in map, action type has to be 'move'")
                else:
                    general['init'] = True
                    text = 'Move your army'
            if general['init'] is True:
                finded = self.locate_reference_img(on_map)
            else:
                finded = Point(0, 0)
            drag = Point(0, 0)
            if mode == Mode.play or mode == Mode.teach_delay:
                if 'drag' in general:
                    if general['init'] is True:
                        drag = (self.coordinations['center_ref'] - finded
                                - Point.from_list(general['relative_coordinates'])) / 3
                        my_pygui.moveTo((self.coordinations['center_ref'] - drag).get())
                        my_pygui.dragTo((self.coordinations['center_ref'] + drag).get())
                    else:
                        my_pygui.moveTo((self.coordinations['center_ref'] - Point.from_list(general['drag'])).get())
                        my_pygui.dragTo((self.coordinations['center_ref'] + Point.from_list(general['drag'])).get())
            elif mode == Mode.teach_co:
                answer = my_pygui.confirm(text='Do You see the target?\n'
                                               ' If not chose \'Drag first\' and drag island to see the target',
                                          title='Teaching Adventure {}'.format(self.name),
                                          buttons=['I see it. Proceed', 'Drag First'])
                if answer == 'Drag First':
                    drag = get_click.get('DRAG')
                    general['drag'] = (drag / 2).get()
            if general['init'] is True:
                if mode == Mode.teach_co:
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    general['relative_coordinates'] = (get_click.get('DOUBLE') - finded - drag).get()
                elif mode == Mode.play or mode == Mode.teach_delay:
                    if 'drag' in general:
                        target = self.coordinations['center_ref'] - drag
                    else:
                        target = Point.from_list(general['relative_coordinates']) + finded
                    if 'delay' in general:
                        if mode == Mode.play:
                            my.wait(general['delay'], 'Next general attacks')
                        elif mode == Mode.teach_delay:
                            my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                            general['delay'] = int(time.time() - t_0)
                    my_pygui.moveTo(target.get())
                    my_pygui.click(target.get(), clicks=2, interval=0.25)
                    if action['type'] in 'move':
                        self.move_veryfication(target)
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
                    if action['type'] in 'move':
                        self.move_veryfication(target)
                elif mode == Mode.teach_co:
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    xcr, ycr = self.coordinations['center_ref'].get()
                    xrc, yrc = get_click.get('DOUBLE').get()
                    general['relative_coordinates'] = [xcr - xrc, ycr - yrc]
        if mode == Mode.teach_delay or mode == Mode.teach_co:
            with open(my.get_new_filename(self.name), 'w') as f:
                json.dump(self.data, f, indent=2)

    def move_veryfication(self, target):
        x_t, y_t = target.get()
        log.info('verifying if move succeed')
        t0 = time.time()
        while True:
            time.sleep(.7)
            loc = my_pygui.locateOnScreen('resource/confirm_move.png',
                                          confidence=0.8,
                                          region=(x_t - 15, y_t - 55, 30, 50))
            if loc:
                log.info('move verification passed in {} s'.format(time.time()-t0))
                break
            else:
                log.info('move verification false - trying again')
                my_pygui.moveTo(target.get())
                my_pygui.click(target.get(), clicks=2, interval=0.25)

    def locate_reference_img(self, on_map):
        my_pygui.moveTo((self.coordinations['book'] + Point(100, 0)).get())
        finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
        if finded:
            if not on_map:
                my_pygui.moveTo(Point.from_point(finded).get())
                my_pygui.dragTo(self.coordinations['center_ref'].get())
                finded = self.coordinations['center_ref']
        else:
            my_pygui.write('0-----')
            import cv2
            img = cv2.imread('data/{}/loc_reference.png'.format(self.name))
            factor = 142/246
            r_img = cv2.resize(img, (int(img.shape[1] * factor), int(img.shape[0] * factor)))
            r_finded = my_pygui.locateOnScreen(r_img, confidence=0.65)
            if r_finded:
                my_pygui.moveTo(Point.from_point(r_finded).get())
                my_pygui.dragTo(self.coordinations['center_ref'].get())
                my_pygui.write('+++')
                my_pygui.moveTo((self.coordinations['book'] + Point(100, 0)).get())
                finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
            else:
                raise Exception('data/{}/loc_reference.png not found on screen'.format(self.name))
        return finded

    def verify_if_generals_active(self, action):
        self.open_star()
        while True:
            result = True
            for general in action['generals']:
                general_loc = self.generals_loc[general['id']]
                result = result and self.verify_if_general_active(general_loc, general['type'])
            if result:
                log.info('all generals from this action active')
                break
            else:
                log.info('not all generals from this action active - trying again')
                my.wait(1, 'Trying again')

    def end_adventure_(self, delay=0):
        log.info('end_adventure')

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
        log.info('end_adventure')

        my.wait(delay, 'Ending adventure')
        self.open_star()
        my_pygui.click(self.coordinations['first_general'].get())
        my_pygui.click(self.coordinations['close_general'].get())
        # finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
        # if not finded:
        #     raise Exception('data/{}/loc_reference.png not found on screen'.format(self.name))
        end_adventure_co = []
        get_click = listener.GetClick()
        if mode == Mode.teach_co:
            while True:
                t_0 = time.time()
                coord = get_click.get('DOWN')
                if coord == 'right':
                    break
                end_adventure_co.append({"co": (coord - self.coordinations['center_ref']).get(),
                                         "delay": time.time() - t_0})
            with open('data/{}/end_adv_co.json'.format(self.name), 'w') as f:
                json.dump(end_adventure_co, f, indent=2)
        elif mode == Mode.play:
            with open('data/{}/end_adv_co.json'.format(self.name), 'r') as f:
                end_adventure_co = json.load(f)
            for click in end_adventure_co:
                target = Point.from_list(click['co']) + self.coordinations['center_ref']
                if mode == Mode.play:
                    my.wait(click['delay'], 'Next click')
                my_pygui.moveTo(target.get())
                my_pygui.click(target.get(), clicks=1, interval=0.25)


def run(adv, adv_name, delay, gap):
    adv.start_adventure(adv_name, delay=delay)
    adv.send_to_adventure(20, first=0, last=100)
    adv.go_to_adventure(gap)
    # adv.retrench_all(30)
    adv.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
    adv.end_adventure(20, Mode.play)


# Configure().run()
adventure = 'byk'
# adventure = 'WW'
TN = Adventure(adventure)
# run(TN, 'byk', 4*60, 6*60)

# Adventure('Home').make_adventure(delay=6*60)
# TN.make_adventure(delay=3, start=8, stop=137, mode=Mode.play)
# TN.end_adventure(1, Mode.play)
# TN.end_adventure(1000000, Mode.play)
# Adventure('Home').make_adventure(delay=5*60)
# Adventure('Ali Baba i Pierwszy').send_to_adventure(3, 0)
# Adventure('Ali Baba i Pierwszy').go_to_adventure(3)
# Adventure('Ali Baba i Pierwszy').make_adventure(2, start=6, stop=115, mode=Mode.play)
# Adventure('DMK').end_adventure(60*60*3+35, Mode.play)
# Adventure('DMK').end_adventure(60*60*24, Mode.play)
# Adventure('DMK').send_to_adventure(3, 13)
# Adventure('DMK').make_adventure(3, 43, 110, mode=Mode.play)

# while True:
#     Adventure('banici').start_adventure('banici')
#     Adventure('banici').send_to_adventure(3, 0)
#     Adventure('banici').go_to_adventure(7*60)
#     Adventure('banici').make_adventure(30, 0, 114, mode=Mode.play)
#     Adventure('banici').end_adventure(170, mode=Mode.play)
#     Adventure('banici_').make_adventure(12*60, 0, 114, mode=Mode.play)
#     break

# Adventure('banici_').make_adventure(2, 0, 114, mode=Mode.play)
# while True:
#     Adventure('WW').start_adventure('wyspa w')
#     Adventure('WW').send_to_adventure(3, 0)
#     Adventure('WW').go_to_adventure(6*60)
#     Adventure('WW').make_adventure(30, 0, 114, mode=Mode.play)
#     Adventure('WW').end_adventure(120, mode=Mode.play)
#     Adventure('WW_').make_adventure(6*60, 0, 114, mode=Mode.play)
#     break

# Adventure('azyl').start_adventure('nest')
# Adventure('byk').send_to_adventure(3, 0)
# Adventure('azyl').go_to_adventure(7*60)
Adventure('byk').make_adventure(3, 19, 140, mode=Mode.play)

# Adventure('spj_gosc').make_adventure(3)
# Adventure('spj_gosp').send_to_adventure(3)
# Adventure('oblezenie').send_to_adventure(3)
# Adventure('oblezenie').make_adventure(3000)
TN.end_adventure(1000000, Mode.play)
TN = Adventure('traitors')
TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
TN.end_adventure(120, Mode.play)

TN = Adventure('traitors2')
TN.start_adventure('zdrajcy', delay=80)
TN.send_to_adventure(20, first=0, last=1)
Adventure('a_traitors').make_adventure(delay=8 * 60)
TN.send_to_adventure(first=2, last=11)
TN.go_to_adventure(7 * 60)
TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
TN.end_adventure(120, Mode.play)
my.wait(80, '')
for i in range(20):

    TN = Adventure('traitors')
    TN.start_adventure('zdrajcy', delay=0)
    TN.send_to_adventure(20, first=0, last=1)
    Adventure('a_traitors').make_adventure(delay=8 * 60)
    TN.send_to_adventure(first=2, last=11)
    TN.go_to_adventure(7 * 60)
    TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
    TN.end_adventure(120, Mode.play)

    TN = Adventure('traitors2')
    TN.start_adventure('zdrajcy', delay=80)
    TN.send_to_adventure(20, first=0, last=1)
    Adventure('a_traitors').make_adventure(delay=8 * 60)
    TN.send_to_adventure(first=2, last=11)
    TN.go_to_adventure(7 * 60)
    TN.make_adventure(delay=30, start=0, stop=137, mode=Mode.play)
    TN.end_adventure(120, Mode.play)
    my.wait(80, '')

