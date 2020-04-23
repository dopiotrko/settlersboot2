import pyautogui
import logging
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
