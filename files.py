import os


def get_first_free_filename_no(name):
    first_free_filename_no = 0
    while os.path.exists('data/{}/learned{:03}.json'.format(name, first_free_filename_no)):
        first_free_filename_no += 1
    return first_free_filename_no


def get_new_filename(name):
    return 'data/{}/learned{:03}.json'.format(name, get_first_free_filename_no(name))


def get_last_filename(name):
    return 'data/{}/learned{:03}.json'.format(name, get_first_free_filename_no(name) - 1)
