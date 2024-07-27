
import mediapipe as mp
import numpy as np
import cv2 as cv #openCV - open computer vision
import time

def findHands(results, draw=True):
    """find and draw the landmarks on the hand (21 points for 1 hand)"""
    if results.multi_hand_landmarks:#if hand is present in the frame then it returns true
        for handLms in results.multi_hand_landmarks: #cycles through all 21 landmarks
            if draw:
                mpDraw.draw_landmarks(frame, handLms, mpHand.HAND_CONNECTIONS) #draw the connection between landmark
    return frame

def findPosition(frame, results, handNo=0, draw=True):
    """return the x and y coordinates of landmarks on the hand 
    in the format [landmark_id,x_coordinate,y_coordinate]"""
    lmList = []
    if results.multi_hand_landmarks:#if hand is present in the frame then it returns true
        myHand = results.multi_hand_landmarks[handNo]#select hand no zero(from parameter)
        for id, lm in enumerate(myHand.landmark):
            height, width, _ = frame.shape #fetch the height and width of the camera frame
            cx, cy = int(lm.x * width), int(lm.y * height) #find the x and y coordinate with respect to the camera window
            lmList.append([id, cx, cy])
            if draw:
                cv.circle(frame, (cx, cy), 10, (0, 0, 255), cv.FILLED)  # draw big circles on the landmark
    return lmList

def countFinger(lmList: list[list], tipIds: dict) -> int:
    """
    counts the number of opened fingers
    """
    if len(lmList) != 0:
        fingers = 0 
        # only for thumb
        if lmList[list(tipIds.keys())[0]][1] < lmList[list(tipIds.keys())[0] - 1][1]: #if tipIds 4 is left of 3 then open
            fingers+=1
        # for other four fingers
        for key, val in tipIds.items(): #if tipIds of rest 4 fingers if above the tipIds of that finger nimus 2 then open
            if key > 4:
                if lmList[key][2] < lmList[key - 2][2]:
                    fingers+=1
        return fingers


tipIds = {4: b'a', 8: b'b', 12: b'c', 16: b'd', 20: b'e'} # key(tipId) value(turn on signal) pair for each finger tip ids
pTime = cTime = 0 #to calculate fps
video = cv.VideoCapture(0) #capture the camera and store it in a variable
mpHand = mp.solutions.hands #create a hand object from mediapipe
hands = mpHand.Hands(max_num_hands=1)  # specify no of hands
mpDraw = mp.solutions.drawing_utils #specify that we want to draw the the connections on hand

if __name__ == '__main__':
    """main function"""

    while True: #infinite loop for video 
        _, frame = video.read() # turn on the camera ('_' allocates less memory)
        frame=cv.flip(frame,1) #flip the frame horizonotally
        frameRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  #translate the colorspace from BGR to RGB, hands object only uses RGB
        results = hands.process(frameRGB) # Processes an RGB image and returns the hand landmarks of each detected hand
        frame = findHands(results) #draw lines on hand if hand is found
        lmList = findPosition(frame, results, draw=False) #return the position of each landmark
        count = countFinger(lmList, tipIds) #count the number of fingers
        cTime = time.time() #fetch the current system time
        fps = 1 // (cTime - pTime) #calculate fps
        pTime = cTime

        if count==None: #if no hand if present in screen then it returns None, we change it to 0 as per our preference
            count=0

        cv.putText(frame, "Fps"+str(fps), (0, 30), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), thickness=2) #print the fps
        cv.putText(frame, "FINGER " + str(count), (35, 460), cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), thickness=2) #print the count of fingers
        cv.rectangle(frame, (30, 425), (190, 470), (0, 0, 255), thickness=2) #draw the rectangle around finger count
        cv.imshow("LIVE", frame) #display the camera feed on screen
        if cv.waitKey(20) & 0xFF == ord('q'): #check if letter q is pressed for atleast 20 miliseconds then close the camera window 
            break #break out of while loop

    video.release() #release the camera
    cv.destroyAllWindows() #destroy all windows created previously