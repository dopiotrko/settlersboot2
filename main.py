# sudo apt-get install scrot
# pip install opencv-contrib-python
import json
import pickle
import time
import pyautogui as pygui
from pynput import mouse

pygui.PAUSE = 1


class Point:
    def __init__(self, x=0, y=0):
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def from_point(cls, point):
        return cls(point.x, point.y)

    @classmethod
    def from_list(cls, list_):
        return cls(list_[0], list_[1])

    def __str__(self):
        return "({0},{1})".format(self.x, self.y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def get(self):
        print('current coordination:', self.x, self.y)
        return self.x, self.y


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
        # pygui.alert(text=text, title='Configuration', button='OK')
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
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['star'] = getClick.get()

        text = 'Adventures'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['adventures'] = getClick.get()

        text = 'Specialists'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['specialists'] = getClick.get()

        text = 'Any General'
        pygui.alert(text=text, title='Configuration', button='OK')
        getClick.get()

        text = 'Recruit Up'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['r_up'] = getClick.get()
        coordinations['recruit'] = coordinations['r_up'] + Point(-43, -18)
        coordinations['bowmen'] = coordinations['r_up'] + Point(86, -18)
        coordinations['militia'] = coordinations['r_up'] + Point(217, -18)
        coordinations['cavalry'] = coordinations['r_up'] + Point(-43, 35)
        coordinations['longbowman'] = coordinations['r_up'] + Point(86, 35)
        coordinations['soldier'] = coordinations['r_up'] + Point(217, 35)
        coordinations['crossbowman'] = coordinations['r_up'] + Point(-43, 94)
        coordinations['elite_soldier'] = coordinations['r_up'] + Point(86, 94)
        coordinations['cannoneer'] = coordinations['r_up'] + Point(217, 94)

        text = 'Unload'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['unload'] = getClick.get()

        text = 'OK'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['confirm_army'] = getClick.get()

        text = 'Send'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send'] = getClick.get()

        text = 'Cancel Send'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['send_cancel'] = getClick.get()
        coordinations['send_confirm'] = coordinations['send_cancel'] - Point(79, 0)

        text = 'Move'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['move'] = getClick.get()
        coordinations['attack'] = coordinations['move'] - Point(0, 86)

        text = 'Quest Book'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book'] = getClick.get()
        coordinations['start_adventure'] = coordinations['book'] + Point(723, 585)

        text = 'Quest Book Down Arrow'
        pygui.alert(text=text, title='Configuration', button='OK')
        coordinations['book_down'] = getClick.get()

        with open('data/conf.dat', 'wb') as f:
            pickle.dump(coordinations, f)

        pygui.alert(text='End of configuration', title='Configuration', button='OK')


# Configure().run()


class StartAdventure:

    def __init__(self, name, delay=0):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('sleeping for {} sec'.format(count))

        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['adventures'].get())

        star_window_corner = self.coordinations['adventures'] - Point(454, 371)
        loc = pygui.locateOnScreen('data/{}/start_adv.png'.format(name),
                                   region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                   confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/confirm.png'.format(name), confidence=0.9)
        if loc is None:
            print('No adventures {} found.'.format(name))
            raise Exception
        else:
            pygui.click(pygui.center(loc))

# StartAdventure('horseback')


class SetArmy:
    def __init__(self, army):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        pygui.click(self.coordinations['unload'].get())
        for units, quantity in army.items():
            if quantity != 0:
                pygui.click(self.coordinations[units].get())
                pygui.write('{}'.format(quantity))

        pygui.click(self.coordinations['confirm_army'].get())


# SetArmy(10, 12, 13, 14, 15, 16, 17, 18, 19)


class SelectGeneral:
    def __init__(self, general):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)

        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())

        star_window_corner = self.coordinations['specialists'] - Point(137, 400)
        loc = pygui.locateOnScreen('resource/{}.png'.format(general),
                                   region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                   confidence=0.95)
        if loc is None:
            print('No general {} found.'.format(general))
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        self.location = loc


# SelectGeneral('major')
# SelectGeneral('basic')
# SelectGeneral('MSW')
# SelectGeneral('ponury')
# SelectGeneral('veteran')


class SelectLastGeneral:
    def __init__(self, loc):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        xy = self.coordinations['star'].get()
        pygui.moveTo(xy[0], xy[1], .2)
        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())
        pygui.click(loc)


class SendToAdventure:
    def __init__(self, name, delay=0, first=1, last=100):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('sleeping for {} sec'.format(count))
        for general in data['generals']:
            if not(first <= general['id'] <= last):
                continue
            last_general_loc = SelectGeneral(general['name']).location
            SetArmy(general['army'])
            # TODO replace by check if general confirmation succeed
            time.sleep(4)
            SelectLastGeneral(last_general_loc)
            pygui.click(self.coordinations['send'].get())
            pygui.click(self.coordinations['send_confirm'].get())


class GoToAdventure:
    def __init__(self, name, delay=0):
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('sleeping for {} sec'.format(count))
        loc = pygui.locateOnScreen('data/{}/goto_adv.png'.format(name), confidence=0.9)
        if loc is None:
            print('No active adventure {} found on the screen.'.format(name))
            raise Exception
        else:
            loc = pygui.center(loc)
            pygui.click(loc)
            pygui.click(loc.x, loc.y+15)


# StartAdventure("LG")
# SendToAdventure("horseback")
# GoToAdventure("LG")


class TeachAdventure:
    def __init__(self, name):
        with open('data/{}/to_learn.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        getClick = GetClick()
        # TODO temporary way to focus window/to be changed
        pygui.click(3200, 700)
        pygui.write('0')
        pygui.scroll(-3, 3200, 700)
        for action in data['actions']:
            start = time.time()
            text = 'Click OK when You want to make Your action ({}) no {}'\
                .format(action['type'], action['no'])
            pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
            action['delay'] = int(time.time() - start)
            # TODO temporary way to focus window/to be changed
            pygui.click(3200, 700)
            for general in action['generals']:
                last_general_loc = SelectGeneral(general['name']).location
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
                if action['type'] in 'attack':
                    pygui.click(self.coordinations['attack'].get())
                    text = 'Make Your attack no {}'.format(action['no'])
                elif action['type'] in 'move':
                    pygui.click(self.coordinations['move'].get())
                    text = 'Move your army'
                else:
                    print('Unexpected action type ')
                    raise Exception
                answer = pygui.confirm(text='Do You see the target?\n'
                                            ' If not chose \'Drag first\' and drag island to see the target',
                                       title='Teaching Adventure {}'.format('name'),
                                       buttons=['I see it. Proceed', 'Drag First'])
                if answer == 'Drag First':
                    general['drag'] = getClick.get('DRAG')
                # pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                if general['init'] is True:
                    finded = pygui.locateOnScreen('data/{}/loc_reference.png'.format(name), confidence=0.9)
                    if not finded:
                        print('data/{}/loc_reference.png not found on screen'.format(name))
                        raise Exception
                    reference = Point.from_point(pygui.center(finded))
                    pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    general['relative_coordinates'] = (getClick.get('DOUBLE') - reference).get()
                else:
                    pygui.alert(text=text, title='Teaching Adventure {}'.format(name), button='OK')
                    general['relative_coordinates'] = getClick.get('DOUBLE').get()

        with open('data/{}/learned.json'.format(name), 'w') as f:
            json.dump(data, f, indent=2)


# TeachAdventure('LG')
# TeachAdventure('horseback')


class LocateGenerals:
    def __init__(self, name):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        generals = dict()
        pygui.click(self.coordinations['star'].get())
        pygui.click(self.coordinations['specialists'].get())
        for general in data['generals']:
            print(general)
            if general['name'] in generals:
                generals[general['name']].append(general['id'])
            else:
                generals[general['name']] = [general['id']]
        general_loc = 100 * [None]
        for general_type, ids in generals.items():
            star_window_corner = self.coordinations['specialists'] - Point(137, 400)
            locations = pygui.locateAllOnScreen('resource/{}.png'.format(general_type),
                                                region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                                confidence=0.95)
            locations = [pygui.center(loc) for loc in locations]
            for id_ in ids:
                general_loc[id_-1] = locations.pop(0)
        while True:
            try:
                general_loc.remove(None)
            except ValueError:
                break
        self.general_loc = general_loc
        pygui.click(self.coordinations['star'].get())

    def get(self):
        return self.general_loc


# LocateGenerals('horseback')


class MakeAdventure:
    def __init__(self, name, delay=0, start=1, stop=1000):
        with open('data/{}/learned.json'.format(name)) as f:
            data = json.load(f)
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        t_start = time.time()
        count = delay
        while time.time() - t_start < delay:
            count -= 1
            time.sleep(1)
            print('sleeping for {} sec'.format(count))
        pygui.click(3200, 700)
        pygui.write('0')
        pygui.scroll(-3, 3200, 700)
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
                time.sleep(action['delay'])
            print(action['no'], time.asctime(time.localtime(time.time())))
            for general in action['generals']:
                # last_general_loc = SelectGeneral(general['name']).location
                SelectLastGeneral(generals_loc[general['id']-1])
                if not general['preset']:
                    SetArmy(general['army'])
                    # TODO replace by: check if general confirmation succeed
                    if action['type'] in ('unload', 'load'):
                        continue
                    time.sleep(4)
                    # SelectLastGeneral(last_general_loc)
                    SelectLastGeneral(generals_loc[general['id']-1])
                if action['type'] in 'attack':
                    pygui.click(self.coordinations['attack'].get())
                elif action['type'] in 'move':
                    pygui.click(self.coordinations['move'].get())
                else:
                    print('Unexpected action type ')
                    raise Exception
                if 'drag' in general:
                    pygui.moveTo(general['drag'][0])
                    pygui.dragTo(general['drag'][1])
                if general['init'] is True:
                    reference = Point.from_point(pygui.center(pygui.locateOnScreen(
                        'data/{}/loc_reference.png'.format(name), confidence=0.9)))
                    target = Point.from_list(general['relative_coordinates']) + reference
                else:
                    target = Point.from_list(general['relative_coordinates'])
                pygui.moveTo(target.get())
                time.sleep(.2)
                pygui.click(target.get(), clicks=2, interval=0.25)


class EndAdventure:
    def __init__(self, name, delay=0):
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.coordinations = pickle.load(config_dictionary_file)
        start = time.time()
        count = delay
        while time.time() - start < delay:
            count -= 1
            time.sleep(1)
            print('sleeping for {} sec'.format(count))
        pygui.click(self.coordinations['book'].get())
        loc = pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        loc = pygui.locateOnScreen('resource/confirm.png', confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click(pygui.center(loc))
        time.sleep(10)
        loc = pygui.locateOnScreen('data/{}/return_ref.png'.format(name), confidence=0.9)
        if loc is None:
            print('Button not found.')
            raise Exception
        else:
            pygui.click((Point.from_point(pygui.center(loc)) + Point(160, 234)).get())


adventure = 'horseback'

for i in range(4):
    StartAdventure(adventure, delay=60)
    SendToAdventure(adventure, first=1, last=2)
    SendToAdventure(adventure, delay=16*60, first=3, last=5)
    GoToAdventure(adventure, 16*60)
    MakeAdventure(adventure, delay=30)
    EndAdventure(adventure, 60)
