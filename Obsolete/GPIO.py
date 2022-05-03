import RPi.GPIO as GPIO
import time

# acting as a pseudo #define
# motor states as it circles the encoder
MotorStates = {
    "State00" : 0b00,
    "State10" : 0b10,
    "State11" : 0b11,
    "State01" : 0b01
}

#motor direction
Direction = {
    "deploy" : 1,
    "retract": 2
}

GPIO.setmode(GPIO.BOARD)
# water sensor
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
#motor GPIOs
GPIO.setup(12, GPIO.OUT)    #deploy when positive
GPIO.setup(32, GPIO.OUT)    #retract when positive
deployMotor = GPIO.PWM(12, 50)  # channel=12 frequency=50Hz   
retractMotor = GPIO.PWM(32, 50)  # channel=32 frequency=50Hz   
#motor hall sensor inputs
GPIO.setup(36, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   #A
GPIO.setup(38, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   #B

class Motor:
    def __init__(self, state=0b00, count=0):
        self.count = count
        self.state = state
    def increaseCount(self):
        self.count = self.count + 1
    def setCount(self, newcount):
        self.count = newcount
    def decreaseCount(self):
        self.count = self.count - 1
    def setState(self, newstates: MotorStates):
        self.state = newstates

def RunMotor(motor: Motor, newAB):
    # count the movements forward or backwards
    # moving forwards, the motor goes 00-> 10 ->11 -> 01
    if motor.states == MotorStates["State00"]:
        if newAB == 0b10:
            motor.increaseCount
        if newAB == 0b01:
            motor.increaseCount
    if motor.states == MotorStates["State10"]:
        if newAB == 0b11:
            motor.increaseCount
        if newAB == 0b00:
            motor.increaseCount
    if motor.states == MotorStates["State11"]:
        if newAB == 0b01:
            motor.increaseCount
        if newAB == 0b10:
            motor.increaseCount
    if motor.states == MotorStates["State01"]:
        if newAB == 0b00:
            motor.increaseCount
        if newAB == 0b11:
            motor.increaseCount
    motor.setState(newAB)

def getNewAB():
    A = GPIO.input(36)
    B = GPIO.input(38)
    return ((A<<1)+B)

def RunMotorByLength(motor: Motor, direction, turn_amount):
    # info about PWM: https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
    #PWM_Pin.start(dc)                  # start PWM where dc is the duty cycle (0.0 <= dc <= 100.0)
    #PWM_Pin.ChangeFrequency(freq)      # change frequency where freq is the new frequency in Hz
    #PWM_Pin.ChangeDutyCycle(dc)        # change duty cycle where 0.0 <= dc <= 100.0
    #PWM_Pin.stop()                     # stop PWM

    motor = Motor()

    if direction == Direction["deploy"]:
        ControllingMotor = deployMotor
        retractMotor.stop()

    elif direction == Direction["retract"]:
        ControllingMotor = retractMotor
        deployMotor.stop()

    #needs to ease the start to prevent jarring
    ControllingMotor.start(25)
    while(motor.count < 100):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.ChangeDutyCycle(50)
    while(motor.count < 200):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.ChangeDutyCycle(75)
    while(motor.count < 300):
        newAB = getNewAB()
        RunMotor(motor, newAB)
        #reset count to restart count

    #actually deploy or return
    motor.setCount(0)
    ControllingMotor.ChangeDutyCycle(100)
    while(motor.count < turn_amount):
        newAB = getNewAB()
        RunMotor(motor, newAB)
        #reset count to restart count

    
    #needs to ease the start to prevent jarring
    ControllingMotor.ChangeDutyCycle(100)
    while(motor.count < 100):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.ChangeDutyCycle(75)
    while(motor.count < 200):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.ChangeDutyCycle(50)
    while(motor.count < 300):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.ChangeDutyCycle(25)
    while(motor.count < 400):
        newAB = getNewAB()
        RunMotor(motor, newAB)
    ControllingMotor.stop()

    return motor.count, motor.state
