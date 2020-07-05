import time
from pynput import mouse
from my_types import Point


class GetClick:
    coord = Point(0, 0)
    # scroll = Point(0, 0)
    double_click = False

    def on_move(self, x, y):
        # print('Pointer moved to {0}'.format((x, y)))
        return

    def on_down(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.coord = Point(x, y)
        elif button == mouse.Button.right:
            self.coord = 'right'
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
            self.coord = Point(x, y) - self.coord
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
        return self.coord
