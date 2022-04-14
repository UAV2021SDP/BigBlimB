#from CV_OD import *
print('Before Import')

import cv2
import CV_OD_Func

# print('Starting Video Stream')

# stream = cv2.VideoCapture(0)
# Check if the webcam is opened correctly
# if not stream.isOpened():
#     raise IOError("Cannot open webcam")

# print('Opened Stream')

print('Init CVObj')
obj = CV_OD_Func.InitCV()
videostream = CV_OD_Func.InitCam(obj)
frame_rate_calc = 0

while True:
    freq = cv2.getTickFrequency()
    t1 = cv2.getTickCount()
    #cv2.resize(frame, [1280,720])
    frame = CV_OD_Func.RunCV(obj, videostream)
    cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
    cv2.imshow('Test', frame)
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1
    c = cv2.waitKey(1)
    if c == 27:
        break

# stream.release()

CV_OD_Func.EndCV(videostream)

# obj = CVObj()

# for x in range(10):
#     RunCV(obj)

# EndCV(obj.videostream)