import board
import busio
import time
from HSM_Foundations import *
import RPi.GPIO as GPIO
i2c = busio.I2C(board.SCL, board.SDA)

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

#ads = ADS.ADS1115(i2c)
#chan = AnalogIn(ads, ADS.P0, ADS.P1)
#ads.gain = 16

#using this file to test the timers too
startingTime = time.time()
RealStartingTime = time.time()

ENABLE = 25
DIRECTION_A = 24
DIRECTION_B = 23
GPIO.setup(ENABLE, GPIO.OUT)        
GPIO.setup(DIRECTION_A, GPIO.OUT)   
GPIO.setup(DIRECTION_B, GPIO.OUT)
MOTOR_ON = 50
#initing the motor
pwm = GPIO.PWM(ENABLE, 50)
pwm.start0)
GPIO.output(DIRECTION_A, GPIO.HIGH)
GPIO.output(DIRECTION_B, GPIO.LOW)

while(time.time()-RealStartingTime <=1):
    if (time.time() - startingTime >= 0.5):
#        print(chan.value, chan.voltage)
        startingTime = time.time()
        
GPIO.cleanup()
        