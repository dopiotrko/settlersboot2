import pyautogui
import logging
import sys
from my_types import Point, Box

if sys.platform == 'win32':
    # this is to fix memory liking in windows, in original pyautogui.pixel function
    from ctypes import windll


    def _pixel(x, y):
        hdc = windll.user32.GetDC(0)
        color = windll.gdi32.GetPixel(hdc, x, y)
        r = color % 256
        g = (color // 256) % 256
        b = color // (256 ** 2)
        windll.user32.ReleaseDC(0, hdc)
        return r, g, b


    pyautogui.pixel = _pixel


    def _pixelMatchesColor(x, y, expectedRGBColor, tolerance=0):
        pix = _pixel(x, y)
        r, g, b = pix[:3]
        exR, exG, exB = expectedRGBColor[:3]
        return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)


    pyautogui.pixelMatchesColor = _pixelMatchesColor

pyautogui.PAUSE = .7


class Click:
    def __call__(self, *args, **kwargs):
        logging.info('Click: {}, {}'.format(args, kwargs))
        pyautogui.PAUSE = .3
        pyautogui.moveTo(*args)
        result = pyautogui.click(*args, **kwargs)
        pyautogui.PAUSE = .7
        return result


class Write:
    def __call__(self, *args, **kwargs):
        logging.info('Write: {}, {}'.format(args, kwargs))
        return pyautogui.write(*args, **kwargs)


class Center:
    def __call__(self, *args, **kwargs):
        logging.info('Center: {}, {}'.format(args, kwargs))
        return Point(args[0].x + int(args[0].w / 2), args[0].y + int(args[0].h / 2))


class Locateallonscreen:
    def __call__(self, *args, **kwargs):
        center_ = True
        if 'center' in kwargs:
            center_ = kwargs.pop('center')
        logging.info('Locateallonscreen: {}, {}'.format(args, kwargs))
        boxes = pyautogui.locateAllOnScreen(*args, **kwargs)
        if boxes:
            if center_:
                return [Point.from_box_center(box) for box in boxes]
            else:
                return [Box.from_box(box) for box in boxes]
        else:
            return None


class Locateonscreen:
    def __call__(self, *args, **kwargs):
        center_ = True
        if 'center' in kwargs:
            center_ = kwargs.pop('center')
        logging.info('Locateonscreen: {}, {}'.format(args, kwargs))
        box = pyautogui.locateOnScreen(*args, **kwargs)
        if box:
            if center_:
                return Point.from_box_center(box)
            else:
                return Box.from_box(box)
        else:
            return None


class Pixelmatchescolor:
    def __call__(self, *args, **kwargs):
        logging.info('Pixelmatchescolor: {}, {}'.format(args, kwargs))
        return pyautogui.pixelMatchesColor(*args, **kwargs)


class Moveto:
    def __call__(self, *args, **kwargs):
        logging.info('Moveto: {}, {}'.format(args, kwargs))
        return pyautogui.moveTo(*args, **kwargs)


class Hotkey:
    def __call__(self, *args, **kwargs):
        logging.info('Hotkey: {}, {}'.format(args, kwargs))
        return pyautogui.hotkey(*args, **kwargs)


class Alert:
    def __call__(self, *args, **kwargs):
        logging.info('Alert: {}, {}'.format(args, kwargs))
        return pyautogui.alert(*args, **kwargs)


class Press:
    def __call__(self, *args, **kwargs):
        logging.info('Press: {}, {}'.format(args, kwargs))
        return pyautogui.press(*args, **kwargs)


class Scroll:
    def __call__(self, *args, **kwargs):
        logging.info('Scroll: {}, {}'.format(args, kwargs))
        return pyautogui.scroll(*args, **kwargs)


class Confirm:
    def __call__(self, *args, **kwargs):
        logging.info('Confirm: {}, {}'.format(args, kwargs))
        return pyautogui.confirm(*args, **kwargs)


class Dragto:
    def __call__(self, *args, **kwargs):
        logging.info('Dragto: {}, {}'.format(args, kwargs))
        return pyautogui.dragTo(*args, **kwargs)


class ScreenShot:
    def __call__(self, *args, **kwargs):
        logging.info('ScreenShot: {}, {}'.format(args, kwargs))
        return pyautogui.screenshot(*args, **kwargs)


click = Click()
write = Write()
center = Center()
locateAllOnScreen = Locateallonscreen()
locateOnScreen = Locateonscreen()
pixelMatchesColor = Pixelmatchescolor()
moveTo = Moveto()
hotkey = Hotkey()
alert = Alert()
press = Press()
scroll = Scroll()
confirm = Confirm()
dragTo = Dragto()
screenshot = ScreenShot()
