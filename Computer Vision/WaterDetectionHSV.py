import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise Exception("Could not open video device")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


while(1):

    # Take each frame
    _, frame = cap.read()
    height, width = frame.shape[:2]
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    #lower_blue = np.array([110,50,50])
    #upper_blue = np.array([130,255,255])
    lower_blue = np.array([90,100,100])
    upper_blue = np.array([125,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    circle = np.zeros((720,1280), dtype="uint8")
    cv2.circle(circle, (640,360), 75, 255, -1)
    #cv2.imshow("Circle", circle)
    
    # Bitwise-AND mask and original image
    #res = cv2.bitwise_and(frame,frame, mask= mask)
    new_mask = cv2.bitwise_and(circle, circle, mask = mask)
    # Max pixels is 17665
    max = 17665
    pixels = cv2.countNonZero(new_mask)
    print('pixels' + str(pixels))
    cur = (pixels/max)*100
    
    if cur >= 80:
        print ("NO ROCK!!")
        
    else:
        print("ROCK PLS NO SONDE")
    #new_res = cv2.bitwise_and(frame, frame, mask = new_mask)
    cv2.circle(img=frame, center = (640,360), radius = 75, color=(255,0,0), thickness=5)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',new_mask)
    #cv2.imshow('res',new_res)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()