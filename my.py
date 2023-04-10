import os
import time
import json
import my_pygui
from my_types import Action


def get_first_free_filename_no(name):
    first_free_filename_no = 0
    while os.path.exists('data/{}/learned{:03}.json'.format(name, first_free_filename_no)):
        first_free_filename_no += 1
    return first_free_filename_no


def get_new_filename(name):
    return 'data/{}/learned{:03}.json'.format(name, get_first_free_filename_no(name))


def get_last_filename(name):
    no = get_first_free_filename_no(name)
    return 'data/{}/learned{:03}.json'.format(name, no - 1) if no else 'data/{}/learned.json'.format(name)


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


def send_explorer_while_error(func):
    def wrapper_send_explorer_while_error(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print("ERROR: {}".format(e))
            my_pygui.press('esc')
            adv = args[0]
            if adv.check_if_in_island() is False:
                adv.go_to_adventure()
            while True:
                adv.send_explorer_by_client(10)
                adv.buff_by_client(3)
                wait(15*60, 'sending after error in ')
    return wrapper_send_explorer_while_error
