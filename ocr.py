import pytesseract
import cv2 as cv
import logging
import numpy as np
import time


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
    img = image_adjusting(img)
    custom_config = r'-c tessedit_char_whitelist="1234567890/ " --psm 7'
    d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config=custom_config)
    (x, y, w, h) = (d['left'][-1], d['top'][-1], d['width'][-1], d['height'][-1])
    roi = img[y-1:y + h+1, x + 20:x + w]
    custom_config = r'--oem 3 --psm 7 outputbase digits'
    return int(pytesseract.image_to_string(roi, config=custom_config))


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
    custom_config = r'-c tessedit_char_whitelist="1234567890 " --psm 7'
    text = pytesseract.image_to_string(img, config=custom_config).split()
    for word in text:
        if word.isdigit():
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
