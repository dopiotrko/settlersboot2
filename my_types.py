from enum import Enum
import pickle
import logging
import copy
import my

action_types = [{"type": 'move'},
                {"type": 'attack'},
                {"type": 'load'},
                {"type": 'unload'},
                {"type": 'retreat'}
                ]


class Point:
    def __init__(self, x=0, y=0):
        logging.info('Point:__init__:')
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def from_point(cls, point):
        logging.info('Point:from_point:')
        return cls(point.x, point.y)

    @classmethod
    def from_list(cls, list_):
        logging.info('Point:from_list:')
        return cls(list_[0], list_[1])

    @classmethod
    def from_box_center(cls, list_):
        logging.info('Point:from_box_center:')
        return cls(list_[0] + list_[2] / 2, list_[1] + list_[3] / 2)

    def __str__(self):
        logging.info('Point:__str__:')
        return "({0},{1})".format(self.x, self.y)

    def __sub__(self, other):
        logging.info('Point:__sub__:')
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

    def __add__(self, other):
        logging.info('Point:__add__:')
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def get(self):
        logging.info('Point:get:')
        return self.x, self.y

    def __repr__(self):
        logging.info('Point:__repr__:')
        return 'Point(x={}, y={})'.format(self.x, self.y)


class Box:
    def __init__(self, x=0, y=0, w=0, h=0):
        logging.info('Box:__init__:')
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @classmethod
    def from_box(cls, box):
        logging.info('Box:from_box:')
        return cls(box.left, box.top, box.width, box.height)

    def __repr__(self):
        logging.info('Box:__repr__:')
        return 'Box(x={}, y={}, w={}, h={})'.format(self.x, self.y, self.w, self.h)


class Mode(Enum):
    play = 1
    teach_co = 2
    teach_delay = 3


class Adventure:
    def __init__(self, name, description=''):
        logging.info('Adventure:__init__:')
        self.name = name
        self.description = description
        self.generals = list()
        self.actions = list()

    def add_general(self, index, **kwargs):
        logging.info('Adventure:add_general:')
        """inserting general at index, or at the end when index==None"""
        self.generals.insert(index, General(**kwargs))
        self.fix_ids()

    def add_action(self, index, **kwargs):
        logging.info('Adventure:add_action:')
        """inserting general at index, or at the end when index==None"""
        self.actions.insert(index, Action(**kwargs))
        # self.fix_ids()

    def remove_general(self, index):
        logging.info('Adventure:remove_general:')
        popped = self.generals.pop(index)
        self.fix_ids()
        return popped

    def remove_action(self, index):
        logging.info('Adventure:remove_action:')
        popped = self.actions.pop(index)
        # self.fix_ids()
        return popped

    def move_general(self, from_, to):
        logging.info('Adventure:move_general:')
        moving = self.remove_general(from_)
        self.generals.insert(to, moving)
        # self.fix_ids()

    def move_action(self, from_, to):
        logging.info('Adventure:move_action:')
        moving = self.remove_action(from_)
        self.actions.insert(to, moving)
        # self.fix_ids()

    def fix_ids(self):
        logging.info('Adventure:fix_ids:')
        for index, gen in enumerate(self.generals):
            gen.id = index

    def get_generals_names(self):
        logging.info('Adventure:get_generals_names:')
        return [gen.name for gen in self.generals]

    def save(self, path):
        logging.info('Adventure:save:')
        path += '.adv' if path[-4:] != '.adv' else ''
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def open(cls, path):
        logging.info('Adventure:open:')
        with open(path, 'rb') as f:
            return pickle.load(f)

    def fix_actions_no(self):
        for i, action in enumerate(self.actions):
            action.no = i

    def as_json(self):
        self.fix_actions_no()
        json = (
            {
                "generals": [gen.as_json() for gen in self.generals],
                "actions": [act.as_json() for act in self.actions]
            }
        )
        return json


class Action:
    def __init__(self, *args, **kwargs):
        logging.info('Action:__init__:')
        self.no = kwargs.get('no', 0)
        self.type = kwargs.get('type', '')
        self.delay = kwargs.get('delay', 0)
        self.generals = [General(self, **gen) for gen in kwargs.get('generals', [])]

    def get_data_for_table(self, attr):
        # logging.info('Action:get_data_for_table:')
        if attr == 'generals':
            return '\n'.join('{} ({}) [{}]'.format(gen.type, gen.name, gen.id) for gen in self.generals)
        else:
            return getattr(self, attr, False)

    def set_data_from_table(self, attr, value):
        logging.info('Action:set_data_from_table:')
        setattr(self, attr, value)

    def get_generals(self):
        logging.info('Action:get_generals:')
        return self.generals

    def add_general(self, general):
        logging.info('Action:add_general:')
        self.generals.append(copy.deepcopy(general))

    def del_general(self, general):
        logging.info('Action:del_general:')
        self.generals.remove(general)

    def as_json(self):
        json = copy.deepcopy(self.__dict__)
        generals = [gen.as_json() for gen in json['generals']]
        json['generals'] = generals
        return json


class General:
    def __init__(self, *args, **kwargs):
        logging.info('General:__init__:')
        self.keys = ["recruit", "bowmen", "militia",
                     "cavalry", "longbowman", "soldier",
                     "crossbowman", "elite_soldier", "cannoneer"]
        self.id = kwargs.get('id', 0)
        self.type = kwargs.get('type', 'empty')
        self.name = kwargs.get('name', None)
        self.delay = kwargs.get('delay', 0)
        self.preset = kwargs.get('preset', False)
        self.init = kwargs.get('init', False)
        self.army = kwargs.get('army', {})
        self.retreat = kwargs.get('retreat', False)
        self.relative_coordinates = kwargs.get('relative_coordinates', None)
        self.drag = kwargs.get('drag')
        self.parent = args[0] if args else None
        self.capacity = kwargs.get('capacity', 300)
        self.id_ref = None

    def get_units(self, key_or_index):
        logging.info('General:get_units:')
        key = self._key_to_index(key_or_index)
        return self.army[key]

    def set_units(self, key_or_index, value):
        logging.info('General:set_units:')
        key = self._key_to_index(key_or_index)
        self.army[key] = value

    def _key_to_index(self, key_or_index):
        logging.info('General:_key_to_index:')
        assert isinstance(key_or_index, int) or isinstance(key_or_index, str)
        key = key_or_index if isinstance(key_or_index, str) else self.keys[key_or_index]
        return key

    def as_json(self):
        # print(self.__dict__)
        json = {}
        army = {}
        # json['army'].update()
        for key, value in self.__dict__.items():
            if key in ('army', 'preset', 'init', 'id') or value:
                json[key] = value
        for key in json['keys']:
            army[key] = json['army'].setdefault(key, 0)
        json['army'] = army
        del json['keys']
        if 'id_ref' in json:
            del json['id_ref']
        json['delay'] = 0
        return json

    def __getstate__(self):
        """pickle without id_ref"""
        state = self.__dict__.copy()
        del state['id_ref']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        my_generals = my.load_generals()
        for gen in my_generals:
            if gen['name'] == self.name:
                self.capacity = gen['capacity']
                break
        self.id_ref = None

