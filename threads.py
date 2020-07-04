import threading
import my_types
import wx
import logging
import my
import my_pygui
import pickle
from my_types import Point, Mode


class StartAdventure(threading.Thread):
    def __init__(self, parent, delay, adventure):
        threading.Thread.__init__(self)
        self._parent = parent
        self.adventure = adventure
        self.delay = delay
        with open('data/conf.dat', 'rb') as config_dictionary_file:
            self.conf_coord = pickle.load(config_dictionary_file)

    def run(self):
        """Overrides Thread.run. Don't call this directly its called internally
        when you call Thread.start().
        """
        logging.info('start_adventure')

        my.wait(self.delay, 'Starting adventure')

        my_pygui.click(self.conf_coord['star'].get())
        my_pygui.click(self.conf_coord['adventures'].get())

        star_window_corner = self.conf_coord['adventures'] - Point(454, 371)
        loc = my_pygui.locateOnScreen('data/{}/start_adv.png'.format(self.adventure.name),
                                      region=(star_window_corner.x, star_window_corner.y, 600, 400),
                                      confidence=0.85)
        if loc is None:
            raise Exception('No adventures {} found.'.format(self.adventure.name))
        else:
            my_pygui.click(loc.get())
        loc = my_pygui.locateOnScreen('resource/start_adventure.png', confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())
        loc = my_pygui.locateOnScreen('resource/confirm.png'.format(self.adventure.name), confidence=0.9)
        if loc is None:
            raise Exception('Button not found.')
        else:
            my_pygui.click(loc.get())
        evt = my_types.CommunicationEvent(my_types.myCommunicationEVENT, -1, None)
        wx.PostEvent(self._parent, evt)
