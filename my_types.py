from enum import Enum


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
