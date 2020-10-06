#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 15:39:34 2020

@author: alberttenigin
"""

from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import dlib
import cv2
import time
import blinks_utils
import packets_client
  
# Colors used in code:
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
    
LIGHT_GREEN = (100, 255, 100)
LIGHT_RED = (100, 100, 255)

# classifier_body = cv2.CascadeClassifier('/home/alberttenigin/projects/cv/model_data/haarcascade_upperbody.xml')
# classifier_face = cv2.CascadeClassifier('/home/alberttenigin/projects/cv/model_data/haarcascade_frontalface_alt.xml')

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=False, 
    default="/home/alberttenigin/projects/cv/shape_predictor_68_face_landmarks.dat",
	help="path to facial landmark predictor")
args = vars(ap.parse_args())
 
INITIAL = time.time()
LAST_TIME_PRESENT = time.time()
TIME_ABSCENT = 0
LAST_TIME_ABSCENT = time.time()
TIMEST = time.time()

WIDTH = 1200

EYE_AR_THRESHOLD = 0.2
EYE_AR_CONSEC_FRAMES = 2
SLEEPING_CONSEC_FRAMES = 125

COUNTER = 0
COUNTER_OPEN = 0
TOTAL = 0
TOTALS = []
LMB = 0
AMB = 0

IS_PRESENT = True
IS_SLEEPING = False
 
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

vs = VideoStream(src=2).start()

#sock = packets_client.connect_socket()

while True:

    frame = vs.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    rects = detector(gray, 0)
        
    for rect in rects:
        if rect.width() >= WIDTH // 10:
            TIMEST += TIME_ABSCENT
            LAST_TIME_PRESENT = time.time()
            TIME_ABSCENT = 0
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]
            leftEAR = blinks_utils.eye_aspect_ratio(leftEye)
            rightEAR = blinks_utils.eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0
            
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            
            if ear < EYE_AR_THRESHOLD:# and time.time() > LAST_BLINK + 0.5:
                COUNTER_OPEN = 0
                COUNTER += 1
    
                if COUNTER >= SLEEPING_CONSEC_FRAMES:
                       IS_SLEEPING = True
            else:
                COUNTER_OPEN += 1
                if COUNTER >= EYE_AR_CONSEC_FRAMES and COUNTER_OPEN > 2:                
                    TOTAL += 1
                    COUNTER = 0
                    IS_SLEEPING = False
            
            if time.time() > TIMEST + 60:
                TIMEST = time.time()
                LMB = TOTAL
                print('For the last minute there were made ', TOTAL, ' blinks, time: ', TIMEST)
                print('Real time gone: ', time.strftime("%H:%M:%S", time.localtime(time.time() - INITIAL)))
                TOTALS.append(TOTAL)
    
                TOTAL = 0
            IS_PRESENT = True
            if len(TOTALS) > 0:
                AMB = sum(TOTALS)/len(TOTALS)

    if len(rects) == 0:
        TIME_ABSCENT += time.time() - LAST_TIME_ABSCENT
        LAST_TIME_ABSCENT = time.time() 
        IS_PRESENT = False

    frame = blinks_utils.draw_frame(IS_SLEEPING, IS_PRESENT, time.localtime(LAST_TIME_PRESENT), time.localtime(LAST_TIME_ABSCENT),\
                       AMB, LMB, TOTAL, frame, WIDTH)
    if IS_SLEEPING:
        sleeping_message = 'Operator is sleeping!'
        present_message = ''
    else:
        sleeping_message = ''
        if IS_PRESENT:
            present_message = 'Operator is working'
        else: 
            present_message = 'Operator is distracted!'
    
    message = '{} {} Average minute blinks: {}'.format(sleeping_message, present_message, AMB)
    print(message)
   # packets_client.send_message(message, sock)
    cv2.imshow("Blinks detection", frame) 
 
    if cv2.waitKey(10) == 27:
        break

cv2.destroyAllWindows()
vs.stream.release()

if len(TOTALS) > 0:
    print('Average number per minute is: ', (sum(TOTALS) / len(TOTALS)))
