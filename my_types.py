from enum import Enum
import pickle


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

    @classmethod
    def from_box_center(cls, list_):
        return cls(list_[0] + list_[2] / 2, list_[1] + list_[3] / 2)

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
        return self.x, self.y

    def __repr__(self):
        return 'Point(x={}, y={})'.format(self.x, self.y)


class Box:
    def __init__(self, x=0, y=0, w=0, h=0):
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    @classmethod
    def from_box(cls, box):
        return cls(box.left, box.top, box.width, box.height)

    def __repr__(self):
        return 'Box(x={}, y={}, w={}, h={})'.format(self.x, self.y, self.w, self.h)


class Mode(Enum):
    play = 1
    teach_co = 2
    teach_delay = 3


class Adventure:
    def __init__(self, name, description=''):
        self.name = name
        self.description = description
        self.generals = list()

    def add_general(self, index, **kwargs):
        """inserting general at index, or at the end when index==None"""
        self.generals.insert(index, General(**kwargs))
        self.fix_ids()

    def remove_general(self, index):
        popped = self.generals.pop(index)
        self.fix_ids()
        return popped

    def move_general(self, from_, to):
        moving = self.remove_general(from_)
        self.generals.insert(to, moving)
        self.fix_ids()

    def fix_ids(self):
        for index, gen in enumerate(self.generals):
            gen.id = index

    def get_generals_names(self):
        return [gen.name for gen in self.generals]

    def save(self, path):
        path += '.adv' if path[-4:] != '.adv' else ''
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def open(cls, path):
        with open(path, 'rb') as f:
            return pickle.load(f)


class Action:
    def __init__(self, *args, **kwargs):
        self.no = kwargs['no']
        self.type = kwargs['type']
        self.delay = kwargs['delay']
        self.generals = [General(self, **gen) for gen in kwargs['generals']]

    def get_data_for_table(self, attr):
        if attr == 'generals':
            return ', '.join('{} ({})'.format(gen.type, gen.id) for gen in self.generals)
        else:
            return getattr(self, attr, False)

    def set_data_from_table(self, attr, value):
        setattr(self, attr, value)

    def get_generals(self):
        return self.generals


class General:
    def __init__(self, *args, **kwargs):
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
        self.capacity = kwargs.get('capacity', 0)

    def get_units(self, key_or_index):
        key = self._key_to_index(key_or_index)
        return self.army[key]

    def set_units(self, key_or_index, value):
        key = self._key_to_index(key_or_index)
        self.army[key] = value

    def _key_to_index(self, key_or_index):
        assert isinstance(key_or_index, int) or isinstance(key_or_index, str)
        key = key_or_index if isinstance(key_or_index, str) else self.keys[key_or_index]
        return key
