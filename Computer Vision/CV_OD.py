from cProfile import label
import os
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

class CVObj:
    def __init__(self, modeldir='Sample_model', graph='detect.tflite', labels='labelmap.txt', resH=720, resW=1280):
        # Store Model
        self.MODEL_NAME = modeldir
        self.GRAPH_NAME = graph
        self.LABELMAP_NAME = labels

        # Store input data
        self.imW = resW
        self.imH = resH
        self.heightDivs = 3
        self.widthDivs = 3
        self.min_conf_threshold = 0.5

        # Get path to current working directory 
        CWD_PATH = os.getcwd()
        # Path to .tflite file, which contains the model that is used for object detection
        PATH_TO_CKPT = os.path.join(CWD_PATH,self.MODEL_NAME,self.GRAPH_NAME)
        # Path to label map file
        PATH_TO_LABELS = os.path.join(CWD_PATH,self.MODEL_NAME,self.LABELMAP_NAME)

        # Load the label map
        with open(PATH_TO_LABELS, 'r') as f:
            self.labels = [line.strip() for line in f.readlines()]

        # Fix first label
        if self.labels[0] == '???':
            del(self.labels[0])

        # Load the Tensorflow Lite model.
        self.interpreter = Interpreter(model_path=PATH_TO_CKPT)
        self.interpreter.allocate_tensors()

        # Get model details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.height = self.input_details[0]['shape'][1]
        self.width = self.input_details[0]['shape'][2]

        self.floating_model = (self.input_details[0]['dtype'] == np.float32)

        self.input_mean = 127.5
        self.input_std = 127.5

        return None

def RunCV(obj=CVObj):
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()
    videostream = VideoStream(resolution=(obj.imW,obj.imH),framerate=30).start()
    time.sleep(1)

    # Start timer (for calculating frame rate)
    t1 = cv2.getTickCount()

    # Grab frame from video stream
    frame1 = videostream.read()

    # Acquire frame and resize to expected shape [1xHxWx3]
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (obj.width, obj.height))
    input_data = np.expand_dims(frame_resized, axis=0)

    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if obj.floating_model:
        input_data = (np.float32(input_data) - obj.input_mean) / obj.input_std

    # Perform the actual detection by running the model with the image as input
    obj.interpreter.set_tensor(obj.input_details[0]['index'],input_data)
    obj.interpreter.invoke()

    # Retrieve detection results
    boxes = obj.interpreter.get_tensor(obj.output_details[0]['index'])[0] # Bounding box coordinates of detected objects
    classes = obj.interpreter.get_tensor(obj.output_details[1]['index'])[0] # Class index of detected objects
    scores = obj.interpreter.get_tensor(obj.output_details[2]['index'])[0] # Confidence of detected objects

    curItem = 0
    items = []

    for i in range(len(scores)):
        if ((scores[i] > obj.min_conf_threshold) and (scores[i] <= 1.0)):
            
            curItem+=1
            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1,(boxes[i][0] * obj.imH)))
            xmin = int(max(1,(boxes[i][1] * obj.imW)))
            ymax = int(min(obj.imH,(boxes[i][2] * obj.imH)))
            xmax = int(min(obj.imW,(boxes[i][3] * obj.imW)))
            
            cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
            xCenter = (xmin+xmax)/2
            yCenter = (ymin+ymax)/2
        
            items = items + (xCenter, yCenter)

            object_name = obj.labels[int(classes[i])]           
            
            # print("%s: (%d,%d)" % ( object_name, xCenter, yCenter) )
            
            # Draw label
            # object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

    # Calculate framerate
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1

    # Draw framerate in corner of frame
    cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)       

    # All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)


def EndCV(videostream):
    # Clean up
    cv2.destroyAllWindows()
    videostream.stop()
