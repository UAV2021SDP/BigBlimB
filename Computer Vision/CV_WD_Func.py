import cv2
import numpy as np
from CV_OD_Func import VideoStream

def InitWDCam():
    return VideoStream(cam=1).start()

def RunWD(videostream=VideoStream):
    frame = videostream.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Create a circular mask at the center
    circle = np.zeros((720,1280), dtype="uint8")
    cv2.circle(circle, (640,360), 75, 255, -1)

    # Bitwise-AND mask and original image
    new_mask = cv2.bitwise_and(circle, circle, mask = mask)

    # Max pixels is 17665
    max = 17665
    pixels = cv2.countNonZero(new_mask)
    cur = (pixels/max)*100

    if cur >= 80:
        rock = 1
        print ("No Rock Detected")
        
    else:
        rock = 0
        print("Rock Detected")

    #cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',new_mask)

    return rock