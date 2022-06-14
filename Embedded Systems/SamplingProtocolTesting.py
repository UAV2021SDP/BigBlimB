
#imports
from HSM_Foundations import *
import RPi.GPIO as GPIO
import time
import board
import busio
import sys
import smbus
import adafruit_ads1x15.ads1115 as ADS 
from adafruit_ads1x15.analog_in import AnalogIn 

#strain gauge stuff
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0, ADS.P1)
ads.gain = 16
TENSION_LOST = 18
TENSION_FOUND = 50

#water sensor stuff
WATER_SENSOR = 17
GPIO.setup(WATER_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#motor stuff
ENABLE = 25
DIRECTION_A = 23
DIRECTION_B = 24
GPIO.setup(ENABLE, GPIO.OUT)        
GPIO.setup(DIRECTION_A, GPIO.OUT)   
GPIO.setup(DIRECTION_B, GPIO.OUT)
MOTOR_ON = 50
#initing the motor
pwm = GPIO.PWM(ENABLE, 50)
pwm.start(50)

#def deployWinch():
#    #deploy winch
#    GPIO.output(DIRECTION_A, GPIO.HIGH)
#    GPIO.output(DIRECTION_B, GPIO.LOW)

#def retractWinch():
#    #retract winch
#    GPIO.output(DIRECTION_A, GPIO.LOW)
#    GPIO.output(DIRECTION_B, GPIO.HIGH)

#def MotorOn():
#    #turn motor on
#    pwm.ChangeDutyCycle(MOTOR_ON)

#def MotorOff():
#    #turn motor off
#    pwm.ChangeDutyCycle(0)
    
#deploy winch
GPIO.output(DIRECTION_A, GPIO.HIGH)
GPIO.output(DIRECTION_B, GPIO.LOW)

SamplingStates = {"LowerWinch" : 0, "HoldToSample" : 1, "RetractWinch": 2, "FreeWinch" : 3, "LowerUAVRetract" : 4, "LowerUAV" : 5, "Done" : 6, "ManualControl" : 7}
currentState = "LowerWinch"
nextState = 0

startTime = time.time()
RealStartTime = time.time()
printTime = time.time()
endTime = time.time() + 5

errorCount = 0
deployDistance = 0.1

time.sleep(0.2)

while(1):
    if currentState == SamplingStates["LowerWinch"]:
        #if strain is lost and we found water, start to sample
        if (GPIO.input(WATER_SENSOR) == 1):
            print("Water Found! Start to sample")
            nextState = SamplingStates["HoldToSample"]
            deployDistance = time.time() - startTime
            endTime = time.time() + 5
            startTime = time.time()
            #turn motor off
            pwm.ChangeDutyCycle(0)

        #if tension is lost but we didnt find water, we likely hit a rock or shore
        elif (chan.value <= TENSION_LOST) and (GPIO.input(WATER_SENSOR) == 0):
            deployDistance += time.time() - startTime
            print("Tension lost but no water... Deploy time:", deployDistance)
            nextState = SamplingStates["RetractWinch"]
            #end time = currentTime + (currentTime - startTime)
            endTime = (2*time.time()) - startTime
            #retract winch
            GPIO.output(DIRECTION_A, GPIO.LOW)
            GPIO.output(DIRECTION_B, GPIO.HIGH)
            #turn motor on
            pwm.ChangeDutyCycle(MOTOR_ON)
            startTime = time.time()

        #we fully deployed but didnt hit water. Need to lower the UAV more.
        elif (time.time() >= endTime):
            print("Lower winch timed out. Lower UAV more.")
            nextState = SamplingStates["LowerUAVRetract"]
            deployDistance = time.time() - startTime
            endTime = time.time() + deployDistance
            startTime = time.time()
            #retract winch
            GPIO.output(DIRECTION_A, GPIO.LOW)
            GPIO.output(DIRECTION_B, GPIO.HIGH)
            #turn motor on
            pwm.ChangeDutyCycle(MOTOR_ON)
    
    elif currentState == SamplingStates["HoldToSample"]:
        if (time.time() >= endTime):
            print("Finished Sampling")
            nextState = SamplingStates["RetractWinch"]
            startTime = time.time()
            #retract winch
            GPIO.output(DIRECTION_A, GPIO.LOW)
            GPIO.output(DIRECTION_B, GPIO.HIGH)
            #turn motor on
            pwm.ChangeDutyCycle(MOTOR_ON)

    elif currentState == SamplingStates["RetractWinch"]:
        #if the timer ends, we have retracted and are ready to move on.
        if (time.time() - startTime >= deployDistance+0.5):
            print("Finished retracting! All done.")
            deployDistance -= time.time() - startTime
            nextState = SamplingStates["Done"]
            #turn motor off
            pwm.ChangeDutyCycle(0)

        #if tension has increased but we are not fully retracted we have gotten stuck
        elif (chan.value >= TENSION_FOUND):
            errorCount += 1
            print("Got stuck retracting! Error count:", errorCount)
            print("value:", chan.value)
            #try to get it free
            if (errorCount <= 2):
                deployDistance = deployDistance - (time.time() - startTime)
                nextState = SamplingStates["FreeWinch"]
                startTime = time.time()
                endTime = time.time() + 1
                #turn motor on
                pwm.ChangeDutyCycle(MOTOR_ON)
                #deploy winch
                GPIO.output(DIRECTION_A, GPIO.HIGH)
                GPIO.output(DIRECTION_B, GPIO.LOW)
            #give up and go to manual mode.
            else:
                print("too stuck, going to manual mode")
                nextState = SamplingStates["ManualControl"]
                #turn motor off
                pwm.ChangeDutyCycle(0)

    elif currentState == SamplingStates["FreeWinch"]:
        if (time.time() >= endTime):
            print("finished trying to free winch, retract again")
            nextState = SamplingStates["RetractWinch"]
            deployDistance += 2
            #retract winch
            GPIO.output(DIRECTION_A, GPIO.LOW)
            GPIO.output(DIRECTION_B, GPIO.HIGH)
            #turn motor on
            pwm.ChangeDutyCycle(MOTOR_ON)
    
    elif currentState == SamplingStates["LowerUAVRetract"]:
        if (time.time() > endTime):
            print("Finished retracting, Lower UAV")
            nextState = SamplingStates["LowerUAV"]
            startTime = time.time()
            endTime = time.time() + 5
            #turn motor off
            pwm.ChangeDutyCycle(0)

    elif currentState == SamplingStates["LowerUAV"]:
        if (time.time() > endTime):
            print("Finished lowering UAV, redeploy.")
            nextState = SamplingStates["LowerWinch"]
            startTime = time.time()
            endTime = time.time() + deployDistance
            #deploy winch
            GPIO.output(DIRECTION_A, GPIO.HIGH)
            GPIO.output(DIRECTION_B, GPIO.LOW)
            #turn motor on
            pwm.ChangeDutyCycle(MOTOR_ON)
            time.sleep(0.2)

    elif currentState == SamplingStates["Done"]:
        #turn motor off
        pwm.ChangeDutyCycle(0)
        
    elif currentState == SamplingStates["ManualControl"]:
        #turn motor off
        pwm.ChangeDutyCycle(0)

    currentState = nextState
    
    if (time.time() - printTime > 0.5):
        print("strain gauge:", chan.value, "water sensor", GPIO.input(WATER_SENSOR))
        printTime = time.time()



