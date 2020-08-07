#!/usr/bin/env python
# coding: utf8
'''
    Author: Şahin Eğilmez <segilmez@outlook.com>
'''

import cv2
import dlib
import numpy as np
import face_recognition
from random import shuffle
from PIL import ImageFont, ImageDraw, Image
from operator import attrgetter
import time
import copy


WINDOW_NAME = "AR KELIME OYUNU"
DISTANCE_OF_LETTER = 2
MASK_TRESHOLD = 10
MOD = 2
PLAYER_NUMBER = 3
FACE_W = 100
FACE_H = 100
HEIGHT = 480
WIDTH = 640


def read_transparent_png(letter):  # read transparent png  and return new image [NOT USING]
    filename = letter.img
    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    image_4channel = cv2.resize(image_4channel, (FACE_W, FACE_H))
    alpha_channel = image_4channel[:, :, 3]
    rgb_channels = image_4channel[:, :, :3]

    # Alpha factor
    alpha_factor = alpha_channel[:, :, np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

    # Transparent Image Rendered on White Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    final_image = base
    return final_image.astype(np.uint8)


def mse(imageA, imageB):  # perform to 'Mean Squared Error' for comapring images
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def compare_faces(self, img2):  # compares to 2 images
    encode1 = face_recognition.face_encodings(img1)
    if(len(encode1) > 0):
        img1_encoding = encode1[0]
    else:
        return False
    img2_encoding = face_recognition.face_encodings(img2)
    if(len(encode1) > 0):
        img1_encoding = encode1[0]
    else:
        return False
    results = face_recognition.compare_faces([img1_encoding], img2_encoding)
    return results[0]
