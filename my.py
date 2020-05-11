import os
import time


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
