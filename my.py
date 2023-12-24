import os
import time
import json
import my_pygui
import logging as log
from my_types import Action
import pygetwindow as pgw
import subprocess


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


def restart_compiled_client_if_gone():
    log.info('restart_client')
    close_not_responding_windows()
    client_window = pgw.getWindowsWithTitle('Nowa Ziemia')
    if len(client_window) == 1:
        log.info('client window exist')
        client_window[0].maximize()
        return
    else:
        subprocess.Popen('C:/Users/dopiotrko/AppData/Local/Ubisoft/Client.exe')
        wait(5)
        client_window = pgw.getWindowsWithTitle('TSO Game Client')
        if len(client_window) == 1:
            log.info('compiled client window opened')
            client_window[0].moveTo(0, 0)
            my_pygui.click(130, 290)
            wait(60, 'maximalising client in')
            restart_compiled_client_if_gone()


def minimize_irrelevant_windows(*args):
    windows = pgw.getWindowsAt(args[0].x, args[0].y)
    for window in windows:
        if 'The Settlers Online' in window.title:
            return
        window.minimize()


def restart_client_if_gone():
    log.info('restart_client')
    close_not_responding_windows()
    client_window = pgw.getWindowsWithTitle('Nowa Ziemia')
    if len(client_window) == 1:
        log.info('client window exist')
        # client_window = client_window[0]
    else:
        settlers_main_page = pgw.getWindowsWithTitle('The Settlers Online')
        if len(settlers_main_page) == 1:
            log.info('main page exist')
            settlers_main_page = settlers_main_page[0]
            settlers_main_page.maximize()
            minimize_irrelevant_windows(settlers_main_page.center)
            my_pygui.click(settlers_main_page.center)
            my_pygui.hotkey('F5')
            wait(10)
            loc = my_pygui.locateOnScreen('resource/pre_login_on_main_page.png')
            if loc:
                my_pygui.click(loc.get())
                wait(5)
            loc = my_pygui.locateOnScreen('resource/ubisoft_on_main_page.png')
            if loc:
                loc = my_pygui.locateOnScreen('resource/active_login_on_main_page.png')
                if loc:
                    my_pygui.click(loc.get())
                    wait(5)
                    loc = my_pygui.locateOnScreen('resource/confirm_on_main_page.png')
                    if loc:
                        my_pygui.click(loc.get())
                    if not loc:
                        loc = my_pygui.locateOnScreen('resource/un_active_login_on_main_page.png')
                        if loc:
                            log.info('logged out - so logging in')
                            my_pygui.click(loc.get())
                            wait(5)
                            my_pygui.click(settlers_main_page.centerx, loc.y + 75)
                            wait(3)
                            my_pygui.click(settlers_main_page.centerx, loc.y + 155)
                            wait(3)
                            my_pygui.click(settlers_main_page.centerx, loc.y + 295)
                            wait(10)
            loc = my_pygui.locateOnScreen('resource/play_on_main_page.png')
            if loc:
                client_window = None
                while not client_window:
                    log.info('play founded')
                    my_pygui.click(loc.x - 68, loc.y - 71)
                    my_pygui.click(loc.x, loc.y - 104)
                    wait(60, 'maximalising client in')
                    client_window = pgw.getWindowsWithTitle('Nowa Ziemia')
                    if close_not_responding_windows():
                        restart_client_if_gone()

                client_window[0].maximize()


def close_not_responding_windows():
    not_responding_windows = pgw.getWindowsWithTitle('Not Responding')
    if len(not_responding_windows) > 0:
        log.info('not_responding_window exist - closing all')
        for n_r_win in not_responding_windows:
            n_r_win.close()
            loc = my_pygui.locateOnScreen('resource/close_not_responding.png')
            if loc:
                my_pygui.click(loc.get())
                log.info('not_responding_window closed')
        return True
    else:
        log.info('all window responding')
        return False


def send_explorer_while_error(func):
    def wrapper_send_explorer_while_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("ERROR: {}".format(e))
            my_pygui.press('esc')
            adv = args[0]
            restart_compiled_client_if_gone()
            while True:
                if not adv.check_if_in_island():
                    adv.go_to_adventure()
                restart_compiled_client_if_gone()
                adv.send_explorer_by_client(10)
                adv.buff_by_client(5, "buffPremium")
                adv.buff_by_client(3, "buffFish")
                my_pygui.hotkey('ctrl', 'm')
                wait(10*60, 'sending after error in ')
    return wrapper_send_explorer_while_error
