import pytesseract
import cv2 as cv
import logging
import numpy as np
import time
import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
lang_en = gettext.translation('settlersbot', localedir, fallback=True, languages=['en'])
lang_pl = gettext.translation('settlersbot', localedir, fallback=True, languages=['pl'])
_ = lang_en.gettext


def image_adjusting(img):
    img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
    resized = cv.resize(img, (img.shape[1] * 4, img.shape[0] * 4), interpolation=cv.INTER_LINEAR)
    _, img_ = cv.threshold(resized, 127, 255, cv.THRESH_BINARY_INV)
    return img_


def data_from_image(img):
    custom_config = r'-c tessedit_char_whitelist="1234567890/ " --psm 6'
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=custom_config)
    # rewriting d to smaller h (only interesting data)
    have = dict((key, []) for key in d.keys())
    n_boxes = len(d['text'])
    for i in range(n_boxes):
        if int(d['level'][i]) == 5:
            for key in d:
                have[key].append(d[key][i])
    return have


def available_army(img):
    img = image_adjusting(img)
    have = data_from_image(img)
    army = list()
    for i in range(len(have['text'])):
        if i % 2:
            (x, y, w, h) = (have['left'][i], have['top'][i], have['width'][i], have['height'][i])
            roi = img[y-1:y + h+1, x + 20:x + w]
            custom_config = r'--oem 3 --psm 7 outputbase digits'
            army.append(int(pytesseract.image_to_string(roi, config=custom_config)))
    return army


def available_unit(img):
    logging.info('available_unit')
    img = image_adjusting(img)
    img = cut_img_to_available(img)
    custom_config = r'-c tessedit_char_whitelist="1234567890/ " --psm 7'
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=custom_config)
    (x, y, w, h) = (d['left'][-1], d['top'][-1], d['width'][-1], d['height'][-1])
    roi = img[y-1:y + h+1, x + 18:x + w]
    logging.info(d['text'])
    unit_v1 = int(d['text'][-1].split('/')[-1])
    logging.info('unit_v1: {}'.format(unit_v1))
    # custom_config = r'--oem 3 --psm 7 outputbase digits'
    # while True:
    #     try:
    #         unit_v2 = int(pytesseract.image_to_string(roi, config=custom_config))
    #     except ValueError:
    #         roi = roi[:, 1:]
    #     else:
    #         cv.imwrite('{} {} {}.png'.format(x, y, unit_v2), roi)
    #         logging.info('unit_v2: {}'.format(unit_v2))
    #         if unit_v1 == unit_v2:
    #             break
    #         else:
    #             roi = roi[:, 1:]
    logging.info('Available units: {}'.format(unit_v1))
    return unit_v1


def get_border(img):
    """return pixel number of the border between assigned, and available units"""
    height, width, _ = img.shape
    white_line = np.full(((height - 10), 1, 3), 255)
    for i in range(width - 1, 1, -1):
        if np.array_equal(img[5:height - 5, i - 1:i], white_line):
            return i


def cut_img_to_assigned(img):
    return img[:, 0:get_border(img)]


def cut_img_to_available(img):
    return img[:, get_border(img)+1:]


def assigned_army(img):
    img = image_adjusting(img)
    have = data_from_image(img)
    return list(int(no) for i, no in enumerate(have['text']) if not i % 2)


def assigned_unit(img):
    img = image_adjusting(img)
    custom_config = r'-c tessedit_char_whitelist="1234567890/ " --psm 7'
    text = pytesseract.image_to_string(img, config=custom_config).split()
    if text[0].isdigit():
        return int(text[0])
    else:
        logging.error('OCR recognition error: {} is not a digit'.format(text[0]))
        raise Exception


def assigned_unit_sum(img):
    img = image_adjusting(img)
    custom_config = r'-l {} --psm 7'.format(_('lang'))
    text = pytesseract.image_to_string(img, config=custom_config).split()
    for word in text:
        if word.isdigit():
            logging.info('Units sum: {}'.format(word))
            return int(word)
    else:
        logging.error('OCR recognition error: No digit in {}'.format(text))
        raise Exception

"""
t0 = time.time()
img = cv.imread('test.png',0)
print(available_army(img))
print(time.time()-t0)
t0 = time.time()
print(assigned_army(img))
print(time.time()-t0)
t0 = time.time()
img = cv.imread('test1.png',0)
print(assigned_unit(img))
print(time.time()-t0)
t0 = time.time()
img = cv.imread('testSum.png',0)
print(assigned_unit_sum(img))
print(time.time()-t0)
"""
