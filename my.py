import os
import time
import json
import my_pygui
from my_types import Action
import pygetwindow as pgw


def get_first_free_filename_no(name, path):
    first_free_filename_no = 0
    while os.path.exists((path + '{:03}.json').format(name, first_free_filename_no)):
        first_free_filename_no += 1
    return first_free_filename_no


def get_new_filename(name, path='data/{}/learned'):
    return (path + '{:03}.json').format(name, get_first_free_filename_no(name, path))


def get_last_filename(name, path='data/{}/learned'):
    no = get_first_free_filename_no(name, path)
    return (path + '{:03}.json').format(name, no - 1) if no else (path + '.json').format(name)


def wait(delay=0, info=''):
    start = time.time()
    count = delay
    while time.time() - start < delay:
        count -= 1
        time.sleep(1)
        print('\r{} in {}:{:02}'.format(info, int(count / 60), count % 60), end='', flush=True)
    print('')


def load_json(name):
    with open(get_last_filename(name)) as f:
        j_data = json.load(f)
    data = [Action(**action) for action in j_data['actions']]
    return data


def load_generals():
    with open('data/generals.json') as f:
        data = json.load(f)
    return data


def restart_client_if_gone():
    # log.info('restart_client')
    client_window = pgw.getWindowsWithTitle('Nowa Ziemia')
    if len(client_window) == 1:
        # log.info('client window exist')
        client_window = client_window[0]
    else:
        settlers_main_page = pgw.getWindowsWithTitle('The Settlers Online')
        if len(settlers_main_page) == 1:
            # log.info('main page exist')
            settlers_main_page = settlers_main_page[0]
            settlers_main_page.maximize()
            my_pygui.click(settlers_main_page.center)
            my_pygui.hotkey('F5')
            wait(10)
            loc = my_pygui.locateOnScreen('resource/pre_login_on_main_page.png')
            if loc:
                my_pygui.click(loc.get())
                wait(5)
            loc = my_pygui.locateOnScreen('resource/ubisoft_on_main_page.png')
            if loc:
                loc = my_pygui.locateOnScreen('resource/confirm_on_main_page.png')
                if loc:
                    my_pygui.click(loc.get())
                else:
                    loc = my_pygui.locateOnScreen('resource/active_login_on_main_page.png')
                    if not loc:
                        loc = my_pygui.locateOnScreen('resource/un_active_login_on_main_page.png')
                    if loc:
                        # log.info('logged out - so logging in')
                        my_pygui.click(loc.get())
                        wait(5)
                        my_pygui.click(settlers_main_page.centerx, loc.y + 75)
                        wait(3)
                        my_pygui.click(settlers_main_page.centerx, loc.y + 155)
                        wait(3)
                        my_pygui.click(settlers_main_page.centerx, loc.y + 295)
                        wait(5)
            loc = my_pygui.locateOnScreen('resource/play_on_main_page.png')
            if loc:
                # log.info('play founded')
                my_pygui.click(loc.x - 68, loc.y - 71)
                my_pygui.click(loc.x, loc.y - 104)
                wait(60, 'maximalising client in')
                client_window = pgw.getWindowsWithTitle('Nowa Ziemia')
                client_window[0].maximize()


def send_explorer_while_error(func):
    def wrapper_send_explorer_while_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("ERROR: {}".format(e))
            my_pygui.press('esc')
            adv = args[0]
            if not adv.check_if_in_island():
                restart_client_if_gone()
                adv.go_to_adventure()
            while True:
                restart_client_if_gone()
                adv.send_explorer_by_client(10)
                adv.buff_by_client(3)
                wait(15*60, 'sending after error in ')
    return wrapper_send_explorer_while_error
