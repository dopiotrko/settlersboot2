# sudo apt-get install scrot
# sudo apt-get install python3-tk python3-dev
# pip install opencv-contrib-python # in your venv
import json
import pickle
import time
import my_pygui
from pynput import mouse
import logging
import my
from my_types import Point
logging.basicConfig(level=logging.INFO)
STAROPEN = False


class GetClick:
    coord = Point(0, 0)
    dragged_coord = None
    # scroll = Point(0, 0)
    double_click = False

    def on_move(self, x, y):
        # print('Pointer moved to {0}'.format((x, y)))
        return

    def on_down(self, x, y, button, pressed):
        self.coord = Point(x, y)
        if pressed:
            # Stop listener
            return False

    def on_double(self, x, y, button, pressed):
        if not pressed:
            if not self.double_click:
                self.double_click = True
            else:
                self.double_click = False
                self.coord = Point(x, y)
                # Stop listener
                return False

    def on_drag(self, x, y, button, pressed):
        if pressed:
            self.coord = Point(x, y)
        else:
            self.dragged_coord = Point(x, y)
            # Stop listener
            return False

    def on_up(self, x, y, button, pressed):
        if not pressed:
            self.coord = Point(x, y)
            # Stop listener
            return False

    def on_scroll(self, x, y, dx, dy):
        # print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))
        return
    # ...or, in a non-blocking fashion:

    def get(self, action='UP'):
        # my_pygui.alert(text=text, title='Configuration', button='OK')
        # Collect events until released
        time.sleep(.5)
        if action == 'UP':
            on_click = self.on_up
        elif action == 'DOWN':
            on_click = self.on_down
        elif action == 'DOUBLE':
            on_click = self.on_double
        elif action == 'DRAG':
            on_click = self.on_drag
        else:
            print('only UP, DOWN, DOUBLE and DRAG arguments allowed to GrtClick.get method')
            raise Exception
        with mouse.Listener(
                on_move=self.on_move,
                on_click=on_click,
                on_scroll=self.on_scroll) as listener:
            listener.join()
        time.sleep(.5)
        return self.coord if action != 'DRAG' else (self.coord.get(), self.dragged_coord.get())


class Configure:
    @staticmethod
    def run():

        coordinations = dict()
        getClick = GetClick()

        text = 'Star Menu'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star'] = getClick.get()

        text = 'Adventures'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['adventures'] = getClick.get()

        text = 'Specialists'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['specialists'] = getClick.get()

        text = 'Search tex field'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star_txt'] = getClick.get()

        text = 'Any General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        getClick.get()

        text = 'Close General'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        getClick.get()

        text = 'Open same general by clicking him on the map (island)'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['center_ref'] = getClick.get()

        text = 'Recruit Up'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['r_up'] = getClick.get()
        region = (coordinations['r_up'] - Point(116, 46)).get() + (44, 44)
        loc = my_pygui.locateOnScreen('resource/army.png', region=region, confidence=.95)
        coordinations['recruit'] = Point.from_list(loc) + Point(74, 26)
        coordinations['bowmen'] = Point.from_list(loc) + Point(199, 26)
        coordinations['militia'] = Point.from_list(loc) + Point(324, 26)
        coordinations['cavalry'] = Point.from_list(loc) + Point(74, 81)
        coordinations['longbowman'] = Point.from_list(loc) + Point(199, 81)
        coordinations['soldier'] = Point.from_list(loc) + Point(324, 81)
        coordinations['crossbowman'] = Point.from_list(loc) + Point(74, 136)
        coordinations['elite_soldier'] = Point.from_list(loc) + Point(199, 136)
        coordinations['cannoneer'] = Point.from_list(loc) + Point(324, 136)

        text = 'Unload'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['unload'] = getClick.get()

        text = 'OK'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['confirm_army'] = getClick.get()

        text = 'Send'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send'] = getClick.get()

        text = 'Cancel Send'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send_cancel'] = getClick.get()
        coordinations['send_confirm'] = coordinations['send_cancel'] - Point(79, 0)

        text = 'Move'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['move'] = getClick.get()
        coordinations['attack'] = coordinations['move'] - Point(0, 86)

        text = 'Quest Book'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book'] = getClick.get()
        coordinations['start_adventure'] = coordinations['book'] + Point(723, 585)

        text = 'Quest Book Down Arrow'
        my_pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book_down'] = getClick.get()

        with open('data/conf.dat', 'wb') as f:
            pickle.dump(coordinations, f)

        my_pygui.alert(text='End of configuration', title='Configuration', button='OK')


# Configure().run()


class LocateGenerals:
    def __init__(self, name):
        logging.info('LocateGenerals:')

        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        generals = dict()
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        for general in data['generals']:
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
        self.general_loc = general_loc
        my_pygui.click(self.coordinations['star'].get())

    def get(self):
        return self.general_loc


class GroupGeneralsByTypes:
    def __init__(self, name, first, last):
        logging.info('GroupGeneralsByTypes')
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        self.generals = dict()
        # pygui.click(self.coordinations['star'].get())
        # pygui.click(self.coordinations['specialists'].get())
        for general in data['generals']:
            if not(first <= general['id'] <= last):
                continue
            if general['type'] in self.generals:
                self.generals[general['type']].append(general)
            else:
                self.generals[general['type']] = [general]

    def get(self):
        return self.generals


class StartAdventure:

    def __init__(self, name, delay=0):
        logging.info('StartAdventure')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my.wait(delay, 'Starting adventure')

        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['adventures'].get())

        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = my_pygui.locateOnScreen('data/{}/start_adv.png'.format(name),
                                      region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                      confidence=0.85)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))
        loc = my_pygui.locateOnScreen('resource/confirm.png'.format(name), confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            my_pygui.click(my_pygui.center(loc))

# StartAdventure('horseback')


class SetArmy:
    def __init__(self, army):
        logging.info('SetArmy')

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


# SetArmy(10, 12, 13, 14, 15, 16, 17, 18, 19)


class SelectGeneral:
    def __init__(self, general):
        logging.info('SelectGeneral')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

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
        self.location = loc


class SelectLastGeneral:
    def __init__(self, loc):
        logging.info('SelectLastGeneral')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        xy = self.coordinations['star'].get()
        my_pygui.moveTo(xy[0], xy[1], .2)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(loc)


class GetGeneralsByType:
    def __init__(self, general_type, general_name=None):
        logging.info('GetGeneralsByType')
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
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
        self.locations = [my_pygui.center(loc) for loc in locations]

    def get(self):
        return self.locations


class SendGeneralsByType:
    def __init__(self, name, general_type, list_of_dicts_with_generals_of_that_type, general_name=None):

        logging.info('SendGeneralsByType')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

        locations_of_gens_of_that_type = GetGeneralsByType(general_type, general_name).get()
        generals_of_type = list(zip(list_of_dicts_with_generals_of_that_type, locations_of_gens_of_that_type))
        generals_of_type.reverse()
        for item_no, (to_send, available) in enumerate(generals_of_type):
            my_pygui.click(available)
            SetArmy(to_send['army'])
            time.sleep(4)
            SelectLastGeneral(available)
            my_pygui.click(self.coordinations['send'].get())
            my_pygui.click(self.coordinations['send_confirm'].get())
            time.sleep(2)
            if item_no < len(generals_of_type)-1:
                my_pygui.click(self.coordinations['star'].get())
                my_pygui.click(self.coordinations['specialists'].get())


class SendToAdventure:
    def __init__(self, name, delay=0, first=0, last=100):
        logging.info('SendToAdventure')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my.wait(delay, 'Sending to adventure')
        for g_type, generals_of_type in GroupGeneralsByTypes(name, first, last).get().items():
            for general in generals_of_type:
                if 'name' in general:
                    generals_of_type.remove(general)
                    SendGeneralsByType(name, g_type, (general,), general['name'])
            if generals_of_type:
                SendGeneralsByType(name, g_type, generals_of_type)
        my_pygui.click(self.coordinations['star'].get())
        my_pygui.click(self.coordinations['specialists'].get())
        my_pygui.click(self.coordinations['star_txt'].get())
        my_pygui.hotkey('ctrl', 'a')
        my_pygui.press('del')
        my_pygui.click(self.coordinations['star'].get())

# SendGeneralsTypeByType.send('CR')


class SendToAdventureOld:
    def __init__(self, name, delay=0, first=0, last=100):
        logging.info('SendToAdventureOld')

        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my.wait(delay, 'Sending to adventure')
        for general in data['generals']:
            if not(first <= general['id'] <= last):
                continue
            last_general_loc = SelectGeneral(general['type']).location
            SetArmy(general['army'])
            # TODO replace by check if general confirmation succeed
            time.sleep(4)
            SelectLastGeneral(last_general_loc)
            my_pygui.click(self.coordinations['send'].get())
            my_pygui.click(self.coordinations['send_confirm'].get())


class GoToAdventure:
    def __init__(self, name, delay=0):
        logging.info('GoToAdventure')

        my.wait(delay, 'Going to adventure')
        loc = my_pygui.locateOnScreen('data/{}/goto_adv.png'.format(name), confidence=0.85)
        if loc is None:
            print('No active adventure {} found on the screen.'.format(name))
            raise Exception
        else:
            loc = my_pygui.center(loc)
            my_pygui.click(loc)
            my_pygui.click(loc.x, loc.y + 15)


# StartAdventure("LG")
# SendToAdventure("horseback")
# GoToAdventure("LG")


class TeachAdventure:
    def __init__(self, name, start=1, stop=1000):
        logging.info('TeachAdventure')

        with open(my.get_last_filename(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        getClick = GetClick()
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star']-Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        for action in data['actions']:
            if not(start <= action['no'] <= stop):
                continue
            t_start = time.time()
            text = 'Click OK when You want to make Your action ({}) no {}'\
                .format(action['type'], action['no'])
            my_pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
            action['delay'] = int(time.time() - t_start)
            # TODO temporary way to focus window/to be changed
            my_pygui.click(focus_temp_loc.get())
            for general in action['generals']:
                last_general_loc = SelectGeneral(general['type']).location
                if not general['preset']:
                    SetArmy(general['army'])
                    if action['type'] in 'unload':
                        continue
                    elif action['type'] in 'load':
                        continue
                    else:
                        # TODO replace by: check if general confirmation succeed
                        time.sleep(4)
                        SelectLastGeneral(last_general_loc)
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
                                          title='Teaching Adventure {}'.format(name),
                                          buttons=['I see it. Proceed', 'Drag First'])
                if answer == 'Drag First':
                    general['drag'] = getClick.get('DRAG')
                    xm, ym = general['drag'][0]
                    xd, yd = general['drag'][1]
                    general['drag'] = [(xd - xm) / 2, (yd - ym) / 2]
                if general['init'] is True:
                    finded = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(name), confidence=0.9)
                    if not finded:
                        print('data/{}/loc_reference.png not found on screen'.format(name))
                        raise Exception
                    reference = Point.from_point(my_pygui.center(finded))
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    general['relative_coordinates'] = (getClick.get('DOUBLE') - reference).get()
                else:
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    xcr, ycr = self.coordinations['center_ref'].get()
                    xrc, yrc = getClick.get('DOUBLE').get()
                    general['relative_coordinates'] = [xcr - xrc, ycr - yrc]
                if 'delay' in general:
                    general['delay'] = int(time.time() - t_start)

        # with open('data/{}/learned.json'.format(name), 'w') as f:
        with open(my.get_new_filename(name), 'w') as f:
            json.dump(data, f, indent=2)


# TeachAdventure('LG')


class MakeAdventure:
    def __init__(self, name, delay=0, start=1, stop=1000, mode='PLAY'):
        logging.info('MakeAdventure')

        with open('data/{}/learned.json'.format(name)) as f:
        # with open(my.get_last_filename(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        my.wait(delay, 'Making adventure')
        # TODO temporary way to focus window/to be changed
        focus_temp_loc = (self.coordinations['star'] - Point(0, 40))
        my_pygui.click(focus_temp_loc.get())
        my_pygui.write('0')
        my_pygui.scroll(-3, focus_temp_loc.x, focus_temp_loc.y)
        if start == 1:
            generals_loc = LocateGenerals(name).get()
            with open('data/{}/generals_loc.dat'.format(name), 'wb') as generals_loc_file:
                pickle.dump(generals_loc, generals_loc_file)
        else:
            with open('data/{}/generals_loc.dat'.format(name), 'rb') as generals_loc_file:
                generals_loc = pickle.load(generals_loc_file)

        for action in data['actions']:
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
                    my_pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    if mode == 'TEACH':
                        action['delay'] = int(time.time() - t_start)

            print(action['no'], time.asctime(time.localtime(time.time())))
            for general in action['generals']:
                SelectLastGeneral(generals_loc[general['id']])
                if not general['preset']:
                    SetArmy(general['army'])
                    # TODO replace by: check if general confirmation succeed
                    if action['type'] in ('unload', 'load'):
                        continue
                    time.sleep(4)
                    SelectLastGeneral(generals_loc[general['id']])
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
                    loc = my_pygui.locateOnScreen('data/{}/loc_reference.png'.format(name), confidence=0.85)
                    if loc is None:
                        print('data/{}/loc_reference.png not find'.format(name))
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
                with open(my.get_new_filename(name), 'w') as f:
                    json.dump(data, f, indent=2)


class EndAdventure:
    def __init__(self, name, delay=0):
        logging.info('EndAdventure')

        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
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
        loc = my_pygui.locateOnScreen('data/{}/return_ref.png'.format(name), confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            my_pygui.click((Point.from_point(my_pygui.center(loc)) + Point(160, 234)).get())


# Configure().run()
adventure = 'CR'
# SendGeneralsByType(adventure, 'basic')
# print(GroupGeneralsByTypes('CR').get())
TeachAdventure(adventure, start=1, stop=88)

# StartAdventure(adventure, delay=3)
# SendToAdventure(adventure, first=0, last=22)
# GoToAdventure(adventure, 10)
# SendToAdventure(adventure, first=4, last=4)
# SendToAdventure(adventure, first=6, last=6)
# SendToAdventure(adventure, first=5, last=5)
# SendToAdventure(adventure, first=3, last=33)
# GoToAdventure(adventure, 1)
# MakeAdventure(adventure, delay=2, start=1, stop=228)
# EndAdventure(adventure, 60)


# for i in range(4):
#     StartAdventure(adventure, delay=60*3)
#     SendToAdventure(adventure, first=1, last=2)
#     SendToAdventure(adventure, delay=16*60, first=3, last=5)
#     GoToAdventure(adventure, 16*60)
#     MakeAdventure(adventure, delay=60)
#     EndAdventure(adventure, 60)
