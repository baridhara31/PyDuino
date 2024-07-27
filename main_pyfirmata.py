from pyfirmata import Arduino, SERVO
import mediapipe as mp
import numpy as np
import cv2 as cv
import time
import math

def findHands(results, draw=True): #find if landmark is presend or not
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            if draw:
                mpDraw.draw_landmarks(frame, handLms, mpHand.HAND_CONNECTIONS)
    return frame #returns after drawing landmark

def findPosition(frame, results, handNo=0, draw=True): #handNo=0 is for 1 hand (0,1) like this
    lmList = [] #landmark_list->list of all x and y axis of all points
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            height, width, chanel = frame.shape
            cx, cy = int(lm.x * width), int(lm.y * height)
            lmList.append([id, cx, cy])
            if draw:
                cv.circle(frame, (cx, cy), 10, (0, 0, 255), cv.FILLED)  # FOR CIRCLE
    return lmList #return list of all x and y coordinates of each landmark

def countFinger(lmList, tipIds, led=False): #counting fingers and turning on leds
    if len(lmList) != 0: #chech if and hand is in frame or not
        fingers = []
        """only for thumb"""
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]: # x coordinate of 4 is greater than x coordinate of 3-on
            fingers.append(1)
            if led:
                connectArduinoLight(tipIds[0], mode=True)
        else:
            fingers.append(0)
            if led:
                connectArduinoLight(tipIds[0])
        """for other four fingers"""
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]: # y coordinate of top landmark is greater than y coordiante of the two below it-on
                fingers.append(1)
                if led:
                    connectArduinoLight(tipIds[id], mode=True)
            else:
                fingers.append(0)
                if led:
                    connectArduinoLight(tipIds[id])
        print(fingers)
        return fingers.count(1) #returning no of open fingers

def fingerLength(lmList, frame, servo=True):
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        x3, y3 = (x1 + x2) // 2, (y1 + y2) // 2
        if servo:
            length = math.hypot(x2 - x1, y2 - y1)
            servorange = int(np.interp(length, [50, 320], [0, 180]))
            servoBar = int(np.interp(length, [50, 320], [400, 150]))
            cv.circle(frame, (x1, y1), 7, (0, 0, 255), cv.FILLED)
            cv.circle(frame, (x2, y2), 7, (0, 0, 255), cv.FILLED)
            cv.line(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
            cv.circle(frame, (x3, y3), 7, (0, 0, 255), cv.FILLED)
            cv.rectangle(frame, (50, 150), (85, 400), (0, 255, 0), thickness=2)
            cv.rectangle(frame, (50, servoBar), (85, 400), (0, 255, 0), cv.FILLED)
            cv.putText(frame, "DEG "+str(servorange), (50, 135), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), thickness=2)
            if length < 50:
                cv.circle(frame, (x3, y3), 7, (0, 255,  0), cv.FILLED)
            # pin_7.write(servorange)

def connectArduinoLight(id, mode=False): #turn led on or off
    if id == 4:
        if mode:
            pin_2.write(1)
        else:
            pin_2.write(0)
    if id == 8:
        if mode:
            pin_3.write(1)
        else:
            pin_3.write(0)
    if id == 12:
        if mode:
            pin_4.write(1)
        else:
            pin_4.write(0)
    if id == 16:
        if mode:
            pin_5.write(1)
        else:
            pin_5.write(0)
    if id == 20:
        if mode:
            pin_6.write(1)
        else:
            pin_6.write(0)

def connectArduinoServo(servo):
    pin_7.write(servo)

widthCam, heightCam = 1000, 500
tipIds = [4, 8, 12, 16, 20] #tip of fingers
pTime = cTime = 0
video = cv.VideoCapture(0)
"""
video.set(3, widthCam)
video.set(4, heightCam)
"""
mpHand = mp.solutions.hands
hands = mpHand.Hands(max_num_hands=1)  # create a hand object
mpDraw = mp.solutions.drawing_utils
# board = Arduino('COM5')
# pin_2 = board.get_pin('d:2:o')
# pin_3 = board.get_pin('d:3:o')
# pin_4 = board.get_pin('d:4:o')
# pin_5 = board.get_pin('d:5:o')
# pin_6 = board.get_pin('d:6:o')
# pin_7 = board.get_pin('d:7:o')
# pin_7.mode = SERVO

while True:
    success, frame = video.read()
    # frame=cv.flip(frame,1)
    frameRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # hands object only uses RGB
    results = hands.process(frameRGB) #generate landmark on hand joints
    frame = findHands(results)
    lmList = findPosition(frame, results, draw=False) #draw all landmarks on hand
    count = countFinger(lmList, tipIds, led=True) #count fingers
    fingerLength(lmList, frame, servo=True) #draw line and control servo

    cTime = time.time()
    fps = 1 // (cTime - pTime)
    pTime = cTime

    if count==None:
        count=0
        

    cv.putText(frame, "Fps"+str(fps), (0, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), thickness=2)
    cv.putText(frame, "FINGER " + str(count), (35, 460), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), thickness=2)
    cv.rectangle(frame, (30, 425), (190, 470), (0, 0, 255), thickness=2)
    cv.imshow("LIVE", frame)
    if cv.waitKey(20) & 0xFF == ord('q'):
        break

video.release()
cv.destroyAllWindows()