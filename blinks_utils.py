#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 14:16:32 2020

@author: alberttenigin
"""
import imutils
import cv2
import time
from scipy.spatial import distance as dist

# Colors used in code:
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
    
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (100, 100, 255)

def draw_frame(is_sleeping, is_present, ltpresent, ltabscent, amb, lmb, blinks, frame, width):
    lmb = int(lmb)
    left = 10
    middle = width // 2 + 10
    
    layer = 30
    
    if width < 600:
        font_size = 0.5
        font_width = 1
    else:
        if width >= 600 and width <= 1200:
            font_size = 1.0
            font_width = 2
        else:
            if width > 1200:
                font_size = 1.5
                font_width = 3
    
    frame = imutils.resize(frame, width)  
    
    def put_text(text, position, color, sleep):
        if sleep:
            fs, fw = font_size + 1.0, font_width + 1
        else:
            fs, fw = font_size, font_width
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_DUPLEX, fs, color, fw)
            
    
    if is_sleeping:
        put_text("OPERATOR IS SLEEPING", (left, width // 3), RED, True)
    if is_present:
       put_text("Operator is working", (left, layer), GREEN, False)
    else:
        put_text("Operator is distracted!", (left, layer), RED, False)
    put_text("LTPresent {}".format(time.strftime("%H:%M:%S", ltpresent)), (left, layer * 3), LIGHT_GREEN, False)
    put_text("LTAbscent {}".format(time.strftime("%H:%M:%S", ltabscent)), (left, layer * 4), LIGHT_RED, False)
    put_text("Last minute blinks: {}".format(lmb), (middle, layer), BLUE, False)
    put_text("Blinks: {}".format(blinks), (left, layer * 2), BLUE, False)
    put_text("Avg minute blinks: {}".format(amb), (middle,layer * 2), BLUE, False)

    return frame


def eye_aspect_ratio(eye):
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	C = dist.euclidean(eye[0], eye[3])

	ear = (A + B) / (2.0 * C)

	return ear