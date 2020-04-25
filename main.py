# sudo apt-get install scrot
# sudo apt-get install python3-tk python3-dev
# pip install opencv-contrib-python # in your venv
import json
import pickle
import time
import my_pygui
import logging
import my
import listener
from my_types import Point
logging.basicConfig(level=logging.INFO)
STAROPEN = False


class Adventure:
    def __init__(self, name):
        logging.info('Init Adventure:')
        self.name = name
        with open('data/{}/learned.json'.format(name)) as f:
            self.data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

    def locate_generals(self):
        logging.info('locate_generals:')

        generals = dict()
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        for general in self.data['generals']:
            print(general)
            if general['type'] in generals:
                generals[general['type']].append(general['id'])
            else:
                generals[general['type']] = [general['id']]
        general_loc = 100 * [None]
        for general_type, ids in generals.items():
            star_window_corner = self.coordinations['specialists'] - Point(137, 400)
            locations = my_pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                                   region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                                   confidence=0.95)
            locations = [my_pygui.center(loc) for loc in locations]
            for id_ in ids:
                general_loc[id_] = locations.pop(0)
        while True:
            try:
                general_loc.remove(None)
            except ValueError:
                break
        my_pygui.click(self.coordinations['star'].get())

        return general_loc

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

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my.wait(delay, 'Starting adventure')

        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['adventures'].get())

        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = my_pygui.locateOnScreen('data/{}/start_adv.png'.format(self.name),
                                      region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                      confidence=0.85)
        if loc is None:
            print('No adventures {} found.'.format(self.name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(self.name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        loc = my_pygui.locateOnScreen('resource/confirm.png'.format(self.name), confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(self.name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))

    def set_army(self, army):
        logging.info('set_army')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my_pygui.click(self.coordinations['unload'].get())
        for units, quantity in army.items():
            if quantity != 0:
                init_x, y = self.coordinations[units].get()
                for x in range(init_x, init_x-50, -24):
                    if not my_pygui.pixelMatchesColor(x, y, (131, 102, 65), tolerance=10):
                        loc = x, y-7
                        break
                else:
                    print('text field not found')
                    raise Exception

                my_pygui.click(loc)
                my_pygui.write('{}'.format(quantity))

        my_pygui.click(self.coordinations['confirm_army'].get())

    def select_general(self, general):
        logging.info('select_general')

        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())

        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        loc = my_pygui.locateOnScreen('resource/{}.png'.format(general),
                                      region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                      confidence=0.95)
        if loc is None:
            print('No general {} found.'.format(general))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        return loc

    def select_general_by_loc(self, loc):
        logging.info('select_general_by_loc')

        xy = self.coordinations['star'].get()
        my_pygui.moveTo(xy[0], xy[1], .2)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(loc)

    def get_generals_by_type(self, general_type, general_name=None):
        logging.info('get_generals_by_type')

        xy = self.coordinations['star'].get()
        my_pygui.moveTo(xy[0], xy[1], .2)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        general = general_name or general_type
        my_pygui.write(general)
        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        locations = my_pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                               region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                               confidence=0.95)
        return [my_pygui.center(loc) for loc in locations]

    def send_generals_by_type(self, general_type, list_of_dicts_with_generals_of_that_type, general_name=None):
        logging.info('send_generals_by_type')

        locations_of_gens_of_that_type = self.get_generals_by_type(general_type, general_name)
        generals_of_type = list(zip(list_of_dicts_with_generals_of_that_type, locations_of_gens_of_that_type))
        generals_of_type.reverse()
        for item_no, (to_send, available) in enumerate(generals_of_type):
            my_pygui.click(available)
            self.set_army(to_send['army'])
            time.sleep(4)
            self.select_general_by_loc(available)
            my_pygui.click(self.coordinations['send'].get())
            my_pygui.click(self.coordinations['send_confirm'].get())
            time.sleep(2)
            if item_no < len(generals_of_type)-1:
                my_pygui.click(self.coordinations['star'].get())
                my_pygui.click(self.coordinations['specialists'].get())

    def send_to_adventure(self, delay=0, first=0, last=100):
        logging.info('send_to_adventure')

        my.wait(delay, 'Sending to adventure')
        for g_type, generals_of_type in self.group_generals_by_types(first, last).items():
            for general in generals_of_type:
                if 'name' in general:
                    generals_of_type.remove(general)
                    self.send_generals_by_type(g_type, (general,), general['name'])
            if generals_of_type:
                self.send_generals_by_type(g_type, generals_of_type)
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
            print('No active adventure {} found on the screen.'.format(self.name))
            raise Exception
        else:
            loc = my_pygui.center(loc)
            my_pygui.click(loc)
            my_pygui.click(loc.x, loc.y + 15)

    def teach_adventure(self, start=1, stop=1000):
        logging.info('teach_adventure')

        get_click = listener.GetClick()
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star']-Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        for action in self.data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            t_start = time.time()
            text = 'Click OK when You want to make Your action ({}) no {}'\
                .format(action['type'], action['no'])
            my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
            action['delay'] = int(time.time() - t_start)
            # TODO temporary way to focus window/to be changed
            my_pygui.click(focus_temp_loc.get())
            for general in action['generals']:
                last_general_loc = self.select_general(general['type']).location
                if not general['preset']:
                    self.set_army(general['army'])
                    if action['type'] in 'unload':
                        continue
                    elif action['type'] in 'load':
                        continue
                    else:
                        # TODO replace by: check if general confirmation succeed
                        time.sleep(4)
                        self.select_general_by_loc(last_general_loc)
                t_start = time.time()
                if action['type'] in 'attack':
                    my_pygui.click(self.coordinations['attack'].get())
                    text = 'Make Your attack no {}'.format(action['no'])
                elif action['type'] in 'move':
                    my_pygui.click(self.coordinations['move'].get())
                    text = 'Move your army'
                else:
                    print('Unexpected action type ')
                    raise Exception

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
                    finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.9)
                    if not finded:
                        print('data/{}/loc_reference.png not found on screen'.format(self.name))
                        raise Exception
                    reference = Point.from_point(my_pygui.center(finded))
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    general['relative_coordinates'] = (get_click.get('DOUBLE') - reference).get()
                else:
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    xcr, ycr = self.coordinations['center_ref'].get()
                    xrc, yrc = get_click.get('DOUBLE').get()
                    general['relative_coordinates'] = [xcr - xrc, ycr - yrc]
                if 'delay' in general:
                    general['delay'] = int(time.time() - t_start)

        # with open('data/{}/learned.json'.format(self.name), 'w') as f:
        with open(my.get_new_filename(self.name), 'w') as f:
            json.dump(self.data, f, indent=2)

    def make_adventure(self, delay=0, start=1, stop=1000, mode='PLAY'):
        logging.info('make_adventure')

        my.wait(delay, 'Making adventure')
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star'] - Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        if start == 1:
            generals_loc = self.locate_generals()
            with open('data/{}/generals_loc.dat'.format(self.name), 'wb') as generals_loc_file:
                pickle.dump(generals_loc, generals_loc_file)
        else:
            with open('data/{}/generals_loc.dat'.format(self.name), 'rb') as generals_loc_file:
                generals_loc = pickle.load(generals_loc_file)

        for action in self.data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            if not start == action['no']:
                if mode == 'PLAY':
                    my.wait(action['delay'], 'Next action ({})in'.format(action['no']))
                else:
                    t_start = time.time()
                    text = 'Click OK when you want to do {1} ({0}) with generals:\n'.format(action['no'],
                                                                                            action['type'])
                    for gen in action['generals']:
                        text += '{:3} - {:10}\n'.format(gen['id'], gen['type'])
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(self.name), button='OK')
                    if mode == 'TEACH':
                        action['delay'] = int(time.time() - t_start)

            print(action['no'], time.asctime(time.localtime(time.time())))
            for general in action['generals']:
                self.select_general_by_loc(generals_loc[general['id']])
                if not general['preset']:
                    self.set_army(general['army'])
                    # TODO replace by: check if general confirmation succeed
                    if action['type'] in ('unload', 'load'):
                        continue
                    time.sleep(4)
                    self.select_general_by_loc(generals_loc[general['id']])
                if action['type'] in 'attack':
                    my_pygui.click(self.coordinations['attack'].get())
                elif action['type'] in 'move':
                    my_pygui.click(self.coordinations['move'].get())
                else:
                    print('Unexpected action type ')
                    raise Exception
                if 'drag' in general:
                    my_pygui.moveTo((self.coordinations['center_ref'] - Point.from_list(general['drag'])).get())
                    my_pygui.dragTo((self.coordinations['center_ref'] + Point.from_list(general['drag'])).get())
                if general['init'] is True:
                    loc = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(self.name), confidence=0.85)
                    if loc is None:
                        print('data/{}/loc_reference.png not find'.format(self.name))
                        raise Exception
                    reference = Point.from_point(my_pygui.center(loc))
                    target = Point.from_list(general['relative_coordinates']) + reference
                else:
                    target = self.coordinations['center_ref'] - Point.from_list(general['relative_coordinates'])
                my_pygui.moveTo(target.get())
                if 'delay' in general:
                    my.wait(general['delay'], 'Next general attacks')
                else:
                    time.sleep(.2)
                my_pygui.click(target.get(), clicks=2, interval=0.25)
            if mode == 'TEACH':
                with open(my.get_new_filename(self.name), 'w') as f:
                    json.dump(self.data, f, indent=2)

    def end_adventure(self, delay=0):
        logging.info('end_adventure')

        my.wait(delay, 'Ending adventure')
        my_pygui.click(self.coordinations['book'].get())
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        loc = my_pygui.locateOnScreen('resource/confirm.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        time.sleep(20)
        loc = my_pygui.locateOnScreen('data/{}/return_ref.png'.format(self.name), confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            my_pygui.click((Point.from_point(my_pygui.center(loc)) + Point(160, 234)).get())


# Configure().run()
adventure = 'CR'
CR = Adventure(adventure)
# teach_adventure(adventure, 18, 18)
# settlers.start_adventure(delay=3)
# settlers.send_to_adventure(first=0, last=9)
# go_to_adventure(adventure, 10)
# settlers.make_adventure(start=18, stop=19)
# send_to_adventure(adventure, first=4, last=4)
# send_to_adventure(adventure, first=6, last=6)
# send_to_adventure(adventure, first=5, last=5)
# send_to_adventure(adventure, first=3, last=4)
# go_to_adventure(adventure, 1)
CR.make_adventure(delay=2, start=1, stop=228)
# end_adventure(adventure, 60)


# for i in range(4):
#     start_adventure(adventure, delay=60*3)
#     send_to_adventure(adventure, first=1, last=2)
#     send_to_adventure(adventure, delay=16*60, first=3, last=5)
#     go_to_adventure(adventure, 16*60)
#     make_adventure(adventure, delay=60)
#     end_adventure(adventure, 60)
