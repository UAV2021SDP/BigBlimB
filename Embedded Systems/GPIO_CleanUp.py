from HSM_Foundations import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

ENABLE = 25
DIRECTION_A = 24
DIRECTION_B = 23
GPIO.setup(ENABLE, GPIO.OUT)        
GPIO.setup(DIRECTION_A, GPIO.OUT)   
GPIO.setup(DIRECTION_B, GPIO.OUT)

GPIO.cleanup()