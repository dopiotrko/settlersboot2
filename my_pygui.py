import pyautogui
import logging
import sys
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
        if len(pix) == 3 or len(expectedRGBColor) == 3:  # RGB mode
            r, g, b = pix[:3]
            exR, exG, exB = expectedRGBColor[:3]
            return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance)
        elif len(pix) == 4 and len(expectedRGBColor) == 4:  # RGBA mode
            r, g, b, a = pix
            exR, exG, exB, exA = expectedRGBColor
            return (abs(r - exR) <= tolerance) and (abs(g - exG) <= tolerance) and (abs(b - exB) <= tolerance) and (
                        abs(a - exA) <= tolerance)

    pyautogui.pixelMatchesColor = _pixelMatchesColor

pyautogui.PAUSE = 1


class Click:
    def __call__(self, *args, **kwargs):
        logging.info('Click: {}, {}'.format(args, kwargs))
        return pyautogui.click(*args, **kwargs)


class Write:
    def __call__(self, *args, **kwargs):
        logging.info('Write: {}, {}'.format(args, kwargs))
        return pyautogui.write(*args, **kwargs)


class Center:
    def __call__(self, *args, **kwargs):
        logging.info('Center: {}, {}'.format(args, kwargs))
        return pyautogui.center(*args, **kwargs)


class Locateallonscreen:
    def __call__(self, *args, **kwargs):
        logging.info('Locateallonscreen: {}, {}'.format(args, kwargs))
        return pyautogui.locateAllOnScreen(*args, **kwargs)


class Locateonscreen:
    def __call__(self, *args, **kwargs):
        logging.info('Locateonscreen: {}, {}'.format(args, kwargs))
        return pyautogui.locateOnScreen(*args, **kwargs)


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
