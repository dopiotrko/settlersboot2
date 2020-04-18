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
        print('current coordination:', self.x, self.y)
        return self.x, self.y