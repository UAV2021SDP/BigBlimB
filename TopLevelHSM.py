from HSM_Foundations import *
import RPi.GPIO as GPIO
import time

#variable definition
free_winch_counter = 0
sampling_start_time = 0

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Defining top level state machine
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

Top_Level = StateMachine("Top_Level")

# Define Normal states / subSM
Startup_State = State("Startup_State")
Takeoff_Wait_State = State("Takeoff_Wait_State")
Obstacle_Avoidance_State = State("Obstacle_Avoidance_State")
Initial_Water_Detect_State = State("Initial_Water_Detect_State")
Sampling_State = State("Sampling_State")
Water_Detect_State = State("Water_Detect_State")
# Define Error States
Manual_Check_Error_State = State("Manual_Check_Error_State")
Manual_Flight_Error_State = State("Manual_Flight_Error_State")

# Define Top Level Events
No_Sys_Errors_Event = Event("No_Sys_Errors")
Takeoff_MAV_Event = Event("Takeoff_MAV")
Arrived_Sampling_MAV_Event = Event("Arrived_Sampling_MAV")
No_Water_Detect_Event = Event("No_Water_Detect")
Water_Detect_Event = Event("Water_Detect")
Sampling_Error_Event = Event("Sampling_Error")
Timer_Ends_Event = Event("Timer_Ends")
Finished_Sampling_Event = Event("Finished_Sampling")
Manual_Takeover_Event = Event("Manual_Takeover")
Sampling_Completed_Event = Event("Sampling_Completed_Event")
Water_Found_Tension_Lost_Event = Event("Water_Found_Tension_Lost_Event")
Tension_Increased_Event = Event("Tension_Increased_Event")
Tension_Lost_Event = Event("Tension_Lost_Event")
No_Event = Event("No_Event")


# Adding States to Top Level
Top_Level.add_state(Startup_State, initial_state=True)
Top_Level.add_state(Takeoff_Wait_State)
Top_Level.add_state(Obstacle_Avoidance_State)
Top_Level.add_state(Initial_Water_Detect_State)
Top_Level.add_state(Sampling_State)
Top_Level.add_state(Water_Detect_State)
Top_Level.add_state(Manual_Check_Error_State)
Top_Level.add_state(Manual_Flight_Error_State)

# Adding Events to Top Level
Top_Level.add_event(No_Sys_Errors_Event)
Top_Level.add_event(Takeoff_MAV_Event)
Top_Level.add_event(Arrived_Sampling_MAV_Event)
Top_Level.add_event(No_Water_Detect_Event)
Top_Level.add_event(Water_Detect_Event)
Top_Level.add_event(Sampling_Error_Event)
Top_Level.add_event(Timer_Ends_Event)
Top_Level.add_event(Finished_Sampling_Event)
Top_Level.add_event(Manual_Takeover_Event)
Top_Level.add_event(Sampling_Completed_Event)
Top_Level.add_event(Water_Found_Tension_Lost_Event)
Top_Level.add_event(Finished_Sampling_Event)
Top_Level.add_event(Tension_Increased_Event)
Top_Level.add_event(No_Event)

# Defining Top Level Normal Transitions
Top_Level.add_transition(Startup_State, Takeoff_Wait_State, No_Sys_Errors_Event)
Top_Level.add_transition(Takeoff_Wait_State, Obstacle_Avoidance_State, Takeoff_MAV_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Initial_Water_Detect_State, Arrived_Sampling_MAV_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Water_Detect_State, No_Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Obstacle_Avoidance_State, Timer_Ends_Event)
Top_Level.add_transition(Sampling_State, Obstacle_Avoidance_State, Sampling_Completed_Event)

# Defining Error / Manual Transitions
Top_Level.add_transition(Startup_State, Manual_Check_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Takeoff_Wait_State, Manual_Check_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Sampling_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Water_Detect_State, Manual_Flight_Error_State, Manual_Takeover_Event)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# GPIO Stuff
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

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
RampDirection = {
    "rampOn" : 1,
    "rampOff": 2
}

class Motor:
    def __init__(self, state=0b00, count=0):
        self.count = count
        self.state = state
        self.speed = 0
        self.direction = Direction["deploy"]
        self.rampDirection = RampDirection["rampOn"]
        self.startTime = 0
        self.deployMotor = GPIO.PWM(12, 50)   # channel=12 frequency=50Hz   
        self.retractMotor = GPIO.PWM(32, 50)  # channel=32 frequency=50Hz
        self.strainLost = 0
        self.turnTicks = 0
    # changing the position count of the rotary encoder
    def increaseCount(self):
        self.count = self.count + 1
    def setCount(self, newcount):
        self.count = newcount
    def decreaseCount(self):
        self.count = self.count - 1
    def getCount(self):
        return self.count
    # changing the speed of the motor
    def increaseSpeed(self):
        self.speed = self.speed + 20
    def decreaseSpeed(self):
        self.speed = self.speed - 20
    def getSpeed(self):
        return self.speed 
    # changing the speed of the motor
    def setTurnTicks(self, ticks):
        self.turnTicks = ticks
    def getTurnTicks(self):
        return self.turnTicks
    # direction stuff with the motor (deploying or retracting)
    def setDirection(self, direction):
        self.direction = direction
    def getDirection(self):
        return self.direction
    #doing motor stuff
    def getDeployMotor(self):
        return self.deployMotor
    def getRetractMotor(self):
        return self.retractMotor
    def startMotorDirection(self):
        resetStrainLost()
        if self.direction == Direction["deploy"]:
            self.retractMotor.stop()
            self.deployMotor.start(this.speed)
        elif self.direction == Direction["retract"]:
            self.deplotMotor.stop()
            self.retractMotor.start(this.speed)
    def setControllingMotor(self):
        if self.direction == Direction["deploy"]:
            self.retractMotor.stop()
            self.deployMotor.ChangeDutyCycle(self.speed)
        elif self.direction == Direction["retract"]:
            self.deplotMotor.stop()
            self.retractMotor.ChangeDutyCycle(self.speed)
    def stopMotors(self):
        self.retractMotor.stop()
        self.deployMotor.stop()
    # ramp direction stuff with the motor (ramp on or ramp off)
    def setRampDirection(self, rampDirection):
        self.rampDirection = rampDirection
    def getRampDirection(self):
        return self.rampDirection
    # what time did we start at a specific speed?
    def setStartTime(self, time):
        self.startTime = time
    def getStartTime(self):
        return self.startTime
    # the motor state changed from the rotary encoder
    def setState(self, newstates: MotorStates):
        self.state = newstates
    # keeping track of the strain gauge stuff
    def strainLost(self):
        self.strainLost = 1
    def resetStrainLost(self):
        self.strainLost = 0
    def getStrainLost(self):
        return self.strainLost

#global motor variable
motor = Motor()

def RunMotor(newAB):
    # count the movements forward or backwards
    # moving forwards, the motor goes 00-> 10 ->11 -> 01
    if motor.states == MotorStates["State00"]:
        if newAB == 0b10:
            motor.increaseCount()
        if newAB == 0b01:
            motor.increaseCount()
    elif motor.states == MotorStates["State10"]:
        if newAB == 0b11:
            motor.increaseCount()
        if newAB == 0b00:
            motor.increaseCount()
    elif motor.states == MotorStates["State11"]:
        if newAB == 0b01:
            motor.increaseCount()
        if newAB == 0b10:
            motor.increaseCount()
    elif motor.states == MotorStates["State01"]:
        if newAB == 0b00:
            motor.increaseCount()
        if newAB == 0b11:
            motor.increaseCount()
    #update the motor current state for next time
    motor.setState(newAB)

def getNewAB():
    A = GPIO.input(36)
    B = GPIO.input(38)
    return ((A<<1)+B)

def runMotorSM():
    # info about PWM: https://sourceforge.net/p/raspberry-gpio-python/wiki/PWM/
    # PWM_Pin.start(dc)                  # start PWM where dc is the duty cycle (0.0 <= dc <= 100.0)
    # PWM_Pin.ChangeFrequency(freq)      # change frequency where freq is the new frequency in Hz
    # PWM_Pin.ChangeDutyCycle(dc)        # change duty cycle where 0.0 <= dc <= 100.0
    # PWM_Pin.stop()                     # stop PWM

    # self.count = count
    # self.state = state
    # self.speed = 0
    # self.turnTicks = x
    # self.direction = Direction["deploy"]
    # self.rampDirection = RampDirection["rampOn"]
    # self.startTime = 0
    # self.deployMotor = GPIO.PWM(12, 50)  # channel=12 frequency=50Hz   
    # self.retractMotor = GPIO.PWM(32, 50)  # channel=32 frequency=50Hz

    # update the motor based on the current speed and direction
    # always update the rotary encoder to get the new position
    newAB = getNewAB()
    RunMotor(motor, newAB)
    currentTime = time.time()

    #if at any point tension is lost, turn off the motor and post the event
    if ((GPIO.input(STRAINGAUGE) <= TENSIONLOST) or (GPIO.input(STRAINGAUGE) >= TENSIONGAINED)):
        motor.strainLost()                  # save the info as a state
        motor.setStartTimeI(currentTime)    # reset start time and direction, start turning off
        motor.decreaseSpeed()
        motor.setRampDirection(RampDirection["rampOff"])
    
    # this is our first time starting up
    if ((motor.getSpeed() == 0) and (motor.getRampDirection() = RampDirection["rampOn"])):    
        motor.setStartTime(currentTime)
        motor.increaseSpeed()
        motor.startMotorDirection()     #get the motor moving in the appropiate direction
    # we just finished deploying
    elif ((motor.getSpeed() == 0) and (motor.getRampDirection() = RampDirection["rampOff"])):
        motor.stopMotors()
        # check if ever lost strain and if we are touching water, post corresponding event
        if(motor.getDirection() == Direction["deploy"]):
            if(GPIO.input(11) == 1):
                # we are good to start sampling, we found water
                Top_Level.trigger_event(Water_Found_Tension_Lost_Event, "Found water, start sampling\r")
            elif (getStrainLost() == 0):
                    # we never lost tension, need to lower the sensor more.
                    Top_Level.trigger_event(Timer_Ends_Event, "Lower the sensor more, water wasn't found\r")
            else:
                # we lost tension at some point and never found water, move on.
                Top_Level.trigger_event(Tension_Lost_Event, "Tension was lost during deploy, move on\r")
        elif(motor.getDirection() = Direction["retract"]):
            # if we are retracting, did we go all the way or get stuck?
            if (getStrainLost() == 0) or (motor.getCount()<100):
                Top_Level.trigger_event(Timer_Ends_Event, "Motor was fully retracted\r")
            else:
                Top_Level.trigger_event(Tension_Increased_Event, "Motor got stuck during retraction\r")

    # we are either ramping up or ramping down, just wait for time to pass
    elif (motor.getSpeed() < 100):
        # if enough time has passed, redefine new start time and update motor speed
        if (motor.getStartTime() - currentTime >= 0.5):
            if getDirection() == Direction["deploy"]:
                motor.increaseSpeed()
            else if getDirection() == Direction["retract"]:
                motor.decreaseSpeed()
            motor.setStartTime(currentTime)
            setControllingMotor()
    # we got as far as we want, start slowing to stop
    elif ((motor.getSpeed() == 100) and (motor.getStartTime() - currentTime == motor.getTurnTicks())):
        setRampDirection(RampDirection["rampOff"])
        motor.decreaseSpeed()
        motor.setStartTime(currentTime)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Actions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

'''all actions need filling in'''
def Water_CV(data):
    print("--water cv function\r")
    water_found = 0
    if water_found:
        Top_Level.trigger_event(Water_Detect_Event, "Water was detected initially\r")
    else:
        Top_Level.trigger_event(No_Water_Detect_Event, "Water was not detected initially\r")

def Obstacle_Avoidance_CV(data):
    print("--Ongoing_Obstacle_Avoidance_CV function\r")
    # call CV function
    # if you see an event, send a MAVLink msg about the obstacle

def Send_Wonder_Command(data):
    # send MAVLink msg to vehicle
    # start timer
    print("--Send_Wonder_Command & start timer function\r")

def Cancel_Timer(data):
    print("--Cancel timer function\r")
    #check if it is still running before canceling it.

def Send_Hover_Command(data):
    print("--Send hover command function\r")
    #send MAVLink msg to hover in place

def Init_Hold_For_Sampling_SubState(data):
    print("--Start sampling timer function\r")
    sampling_start_time = time.time()
    #start a 30 sec timer

def Init_Hold_For_Sampling_SubState(data):
    if (time.time() - sampling_start_time >= 30):
        print("--Sampling timer is done\r")
        Top_Level.trigger_event(Timer_Ends_Event, "Finished Sampling Timer\r")

def Finished_Sampling(data):
    print("--Finished_Sampling function\r")
    Top_Level.trigger_event(Sampling_Completed_Event, "Finished Sampling\r")

def Init_Lower_Winch_SubState(data):
    print("--Init_Lower_Winch_SubState function\r")
    motor.setDirection(Direction["deploy"])
    motor.setRampDirection(RampDirection["rampOn"])
    motor.setTurnTicks(100)

def Init_Retract_Winch_SubState(data):
    print("--Init_Retract_Winch_SubState function\r")
    motor.setDirection(Direction["retract"])
    motor.setRampDirection(RampDirection["rampOn"])

def Init_Free_Retracting_Winch_SubState(data):
    print("--Init_Free_Retracting_Winch_SubState function\r")
    motor.setDirection(Direction["deploy"])
    motor.setRampDirection(RampDirection["rampOn"])
    motor.setTurnTicks(10)
    free_winch_counter += 1
    if free_winch_counter < 3:
        print("--Increasing winch counter:", free_winch_counter)
    else:
        print("--Deployment error, go to manual\r")
        Top_Level.trigger_event(Manual_Takeover_Event, "Retract Error - go to manual\r")
    
def Init_Lower_UAV_Retract_Winch_SubState(data):
    print("--Init_Lower_UAV_Retract_Winch_SubState function\r")
    motor.setDirection(Direction["retract"])
    motor.setRampDirection(RampDirection["rampOn"])



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Defining lower level state machines
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#if at any state we get the Manual_Takeover_Event, move to manual flight error state

# Startup_State
    #------ vehicle Confirmations ------#
    # confirm batteries are plugged in 
    # have user manually control each actuatorn
    #------ Payload Confirmations ------#
    # initialize OA computer vision
        # call the command and wait for a heartbeat back
    # test and ensure accurate OA reading
        # tell user to stand in front of airship and wait until reading
    # initialize WD computer vision
        # call the command and wait for a heartbeat back
    # test and ensure accurate WD reading
        # call and confirm "no" reading
    # init winch library
    # deploy and retract motor .5ft and confirm with rotary encoder
    # init MAVLink library
    # test and ensure MAVLink heartbeat with vehicle OBC

    # if errors - transition to error manual state
    # else - transition to Takeoff_Wait_State
#Startup_SubSM = StateMachine("Startup_SubSM")
#Startup_State.set_child_sm(Startup_SubSM)
'''needs more work for states and functions once we know'''

# Takeoff_Wait_State
    # if takeoff MAVLink msg from vehicle - transition to Obstacle_Avoidance_State
    # no substate machine needed for this one, just a top level normal transition

# Obstacle_Avoidance_State
    # call CV function 
    # if obstacle, send MAVLink msg to vehicle with hardset distance
    # if recieved begin sampling MAVLink msg from vehicle - transition to Initial_Water_Detect_State
    # can be done within the state - doesnt need sub-subSM
# defining obstacle avoidance null transition
Obstacle_Avoidance_Null_Transition = Top_Level.add_null_transition(Obstacle_Avoidance_State, No_Event)
Obstacle_Avoidance_Null_Transition.add_action(Obstacle_Avoidance_CV)

# Initial_Water_Detect_State
    # call CV function
    # if water detected - transition to Sampling_State
    # else - transition to Water_Detect_State
    # no sub-subSM needed, simply call the function on entry and raise event from it.
Initial_Water_Detect_State.on_entry(Water_CV)

# Sampling_State
    # send "hover" command to vehicle
    # turn winch motor ~12 feet
    # if at any point the sonde touches water
        # keep lowering until tension sensor says it is floating
        # hold for 30 sec
        # raise winch back
    # else, if sonde doesnt touch water
        # if tension sensor says it is still under tension
            # retract winch
            # lower airship by 5 feet
            # reattempt.
        # else 
            # retract winch
            # send "move to next location" command to vehicle and transion to Obstacle_Avoidance_State
    # note: have a sub-substate for retracting winch:
        # attempt to slowly retract winch
        # if tension sensor implies more force before it is finished
            # re-deploy 2 feet and reattempt 3 times max
            # if still stuck after 3 times, switch to manual control error mode.
Sampling_SubSM = StateMachine("Sampling_SubSM")
Sampling_State.set_child_sm(Sampling_SubSM)
Sampling_State.on_entry(Send_Hover_Command)
# define the substates
Lower_Winch_SubState = State("Lower_Winch_SubState")                # lower the winch using the winch SM
Hold_For_Sampling_SubState = State("Hold_For_Sampling_SubState")    # basically just a 30 sec timer to allow for sampling
Retract_Winch_SubState = State("Retract_Winch_SubState")            # raise the winch after sampling
Lower_UAV_Retract_Winch_SubState = State("Lower_UAV_Retract_Winch_SubState")    # raise the winch if we aren't low enough
Lower_UAV_SubState = State("Lower_UAV_SubState")                    # lower the airship by ~10 ft
Finish_SubState = State("Finish_SubState")                          # we are done and ready to leave the SM
Free_Retracting_Winch_SubState = State("Free_Retracting_Winch_SubState")        # re-retract the winch if we got stuck
# add state actions if needed
Hold_For_Sampling_SubState.on_entry(Init_Hold_For_Sampling_SubState)   # start a 30s timer for sampling
Lower_Winch_SubState.on_entry(Init_Lower_Winch_SubState)
Retract_Winch_SubState.on_entry(Init_Retract_Winch_SubState)
Free_Retracting_Winch_SubState.on_entry(Init_Free_Retracting_Winch_SubState)
Lower_UAV_Retract_Winch_SubState.on_entry(Init_Lower_UAV_Retract_Winch_SubState)
Finish_SubState.on_entry(Finished_Sampling)               # finished sampling, move on on the top level
# add substates to subSM
Sampling_SubSM.add_state(Lower_Winch_SubState, initial_state=True)
Sampling_SubSM.add_state(Hold_For_Sampling_SubState)
Sampling_SubSM.add_state(Retract_Winch_SubState)
Sampling_SubSM.add_state(Lower_UAV_Retract_Winch_SubState)
Sampling_SubSM.add_state(Lower_UAV_SubState)
Sampling_SubSM.add_state(Free_Retracting_Winch_SubState)
Sampling_SubSM.add_state(Finish_SubState)
# add transitions
Sampling_SubSM.add_transition(Lower_Winch_SubState, Hold_For_Sampling_SubState, Water_Found_Tension_Lost_Event) # successfully lowered winch
Sampling_SubSM.add_transition(Lower_Winch_SubState, Retract_Winch_SubState, Tension_Lost_Event)                 # winch deployed in incorrect location, retract and move on
Sampling_SubSM.add_transition(Lower_Winch_SubState, Lower_UAV_Retract_Winch_SubState, Timer_Ends_Event)        # winch not lowered enough, retract winch
Sampling_SubSM.add_transition(Lower_UAV_Retract_Winch_SubState, Lower_UAV_SubState, Timer_Ends_Event)          # winch not lowered enough, lower UAV 
Sampling_SubSM.add_transition(Lower_UAV_SubState, Lower_Winch_SubState, Timer_Ends_Event)                      # after lowering, redeploy winch
Sampling_SubSM.add_transition(Hold_For_Sampling_SubState, Retract_Winch_SubState, Timer_Ends_Event)            # successfully sampled
Sampling_SubSM.add_transition(Retract_Winch_SubState, Free_Retracting_Winch_SubState, Tension_Increased_Event)  # winch got stuck, retry
Sampling_SubSM.add_transition(Free_Retracting_Winch_SubState, Retract_Winch_SubState, Timer_Ends_Event)        # attempt to re-retract the winch       
Sampling_SubSM.add_transition(Retract_Winch_SubState, Finish_SubState, Timer_Ends_Event)                       # finished sampling successfully, move on :)
# defining null transitions
Retract_Winch_Null_Transition = NullTransition(Retract_Winch_SubState, No_Sys_Errors_Event)    
Lower_Winch_Null_Transition = NullTransition(Lower_Winch_SubState, No_Sys_Errors_Event) 
Free_Winch_Retract_Null_Transition = NullTransition(Free_Retracting_Winch_SubState, No_Sys_Errors_Event)    
Lower_UAV_Winch_Retract_Null_Transition = NullTransition(Lower_UAV_Retract_Winch_SubState, No_Sys_Errors_Event)    
Hold_For_Sampling_SubState_Null_Transition =  NullTransition(Hold_For_Sampling_SubState, No_Sys_Errors_Event)    
# adding action to null transitions
Retract_Winch_Null_Transition.add_action(runMotorSM)
Lower_Winch_Null_Transition.add_action(runMotorSM)
Free_Winch_Retract_Null_Transition.add_action(runMotorSM)
Lower_UAV_Winch_Retract_Null_Transition.add_action(runMotorSM)
Hold_For_Sampling_SubState_Null_Transition.add_action(Init_Hold_For_Sampling_SubState)
# add the null transitions to the SM
Sampling_SubSM.add_transition(Retract_Winch_Null_Transition)
Sampling_SubSM.add_transition(Lower_Winch_Null_Transition)
Sampling_SubSM.add_transition(Free_Winch_Retract_Null_Transition)
Sampling_SubSM.add_transition(Lower_UAV_Winch_Retract_Null_Transition)
Sampling_SubSM.add_transition(Hold_For_Sampling_SubState_Null_Transition)

# Water_Detect_State
    # start timer and send "wander for x seconds" MAVLink command to vehicle
    # run water CV function on repeat for x seconds 
    # if water detected - cancel timer and transition to Sampling_State
    # else if timer ended - send "move to next location" command to vehicle and transition to Obstacle_Avoidance_State
    #doesnt need sub-subSM, can do within state.
# add actions for entry and exit
Water_Detect_State.on_entry(Send_Wonder_Command) # send MAVLink msg to wander and start timer
# add water detect null transition
Water_Detect_Null_Transition = Top_Level.add_null_transition(Water_Detect_State, No_Event)
Water_Detect_Null_Transition.add_action(Water_CV)



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

GPIO.setmode(GPIO.BOARD)
# water sensor
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
#motor GPIOs
GPIO.setup(12, GPIO.OUT)    #deploy when positive
GPIO.setup(32, GPIO.OUT)    #retract when positive
#motor hall sensor inputs
GPIO.setup(36, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   #A
GPIO.setup(38, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)   #B

#motor stuff later
if direction == Direction["deploy"]:
        ControllingMotor = deployMotor
        retractMotor.stop()

elif direction == Direction["retract"]:
    ControllingMotor = retractMotor
    deployMotor.stop()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# Test Harness
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

Top_Level_Event_Dict = {
    "No_Sys_Errors" : No_Sys_Errors_Event,
    "Takeoff_MAV" : Takeoff_MAV_Event,
    "Arrived_Sampling_MAV" : Arrived_Sampling_MAV_Event,
    "No_Water_Detect" : No_Water_Detect_Event,
    "Water_Detect" : Water_Detect_Event,
    "Sampling_Error" : Sampling_Error_Event,
    "Timer_Ends" : Timer_Ends_Event,
    "Manual_Takeover" : Manual_Takeover_Event,
    "Sampling_Completed_Event" : Sampling_Completed_Event,
    "Water_Found_Tension_Lost_Event" : Water_Found_Tension_Lost_Event,
    "Finished_Sampling_Event" : Finished_Sampling_Event,
    "Tension_Increased_Event" : Tension_Increased_Event,
    "No_Event" : No_Event
}

def PrintEntryState(data):
    print("Top Level Entry:", Top_Level._current_state.name, " Data:", data)

# top level states 
Startup_State.on_entry(PrintEntryState)
Takeoff_Wait_State.on_entry(PrintEntryState)
Obstacle_Avoidance_State.on_entry(PrintEntryState)
Initial_Water_Detect_State.on_entry(PrintEntryState)
Sampling_State.on_entry(PrintEntryState)
Water_Detect_State.on_entry(PrintEntryState)
Manual_Check_Error_State.on_entry(PrintEntryState)
Manual_Flight_Error_State.on_entry(PrintEntryState)

Top_Level.start("Hello World")

while(1):
    user_event = input("Enter an event: ")
    Top_Level.trigger_event(Top_Level_Event_Dict[user_event], user_event)
