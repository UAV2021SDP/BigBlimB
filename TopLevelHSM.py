from HSM_Foundations import *

#variable definition
free_winch_counter = 0

#~~~~~~~~~~~~~~~~~~~~~~~~ defining top level state machine ~~~~~~~~~~~~~~~~~~~~~~~~#

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
Top_Level.add_event(No_Event)

# Defining Top Level Normal Transitions
Top_Level.add_transition(Startup_State, Takeoff_Wait_State, No_Sys_Errors_Event)
Top_Level.add_transition(Takeoff_Wait_State, Obstacle_Avoidance_State, Takeoff_MAV_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Initial_Water_Detect_State, Arrived_Sampling_MAV_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Water_Detect_State, No_Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Obstacle_Avoidance_State, Timer_Ends_Event)
Top_Level.add_transition(Sampling_State, Obstacle_Avoidance_State, Timer_Ends_Event)

# Defining Error / Manual Transitions
Top_Level.add_transition(Startup_State, Manual_Check_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Takeoff_Wait_State, Manual_Check_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Sampling_State, Manual_Flight_Error_State, Manual_Takeover_Event)
Top_Level.add_transition(Water_Detect_State, Manual_Flight_Error_State, Manual_Takeover_Event)


#~~~~~~~~~~~~~~~~~~~~~~ defining lower level state machines ~~~~~~~~~~~~~~~~~~~~~~~#

#Actions:
'''all actions need filling in'''
def Water_CV(data):
    #water_found = 0
    #if water_found:
    #    Top_Level.trigger_event(Water_Detect_Event, "Water was detected intially")
    #else:
    #    Top_Level.trigger_event(No_Water_Detect_Event, "Water was not detected intially")
    print("water cv function\r")

def Obstacle_Avoidance_CV(data):
    print("Ongoing_Obstacle_Avoidance_CV function\r")
    # call CV function
    # if you see an event, send a MAVLink msg about the obstacle

def Send_Wonder_Command(data):
    # send MAVLink msg to vehicle
    # start timer
    print("Send_Wonder_Command & start timer function\r")

def Cancel_Timer(data):
    print("cancel timer function\r")
    #check if it is still running before canceling it.

def Send_Hover_Command(data):
    print("send hover command function\r")
    #check if it is still running before canceling it.

def Start_Sample_Timer(data):
    print("Start sampling timer function\r")
    #start a 30 sec timer

def Increase_Free_Winch_Counter(data):
    try:
        free_winch_counter += 1
    except:
        free_winch_counter = 0
    print("Increasing winch counter:", free_winch_counter, "function\r")

#if at any state we get the Manual_Takeover_Event, move to manual flight error state

# Startup_State
    # initialize computer vision
    # test and ensure accurate reading
    # init winch library
    # test and ensure accurate reading
    # init MAVLink library
    # test and ensure heartbeat
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
Lower_Winch_SubState = State("Lower_Winch_SubState")
Hold_For_Sampling_SubState = State("Hold_For_Sampling_SubState")
Retract_Winch_SubState = State("Retract_Winch_SubState")
Lower_UAV_Retract_Winch_SubState = State("Lower_UAV_Retract_Winch_SubState")
Lower_UAV_SubState = State("Lower_UAV_SubState")
Finish_SubState = State("Finish_SubState")
Error_SubState = State("Error_SubState")
Free_Retracting_Winch_SubState = State("Free_Retracting_Winch_SubState")
# add state actions if needed
Hold_For_Sampling_SubState.on_entry(Start_Sample_Timer)   # start a 30s timer for sampling
Free_Retracting_Winch_SubState.on_entry(Increase_Free_Winch_Counter)   # start a 30s timer for sampling
# add substates to subSM
Sampling_SubSM.add_state(Lower_Winch_SubState, initial_state=True)
Sampling_SubSM.add_state(Hold_For_Sampling_SubState)
Sampling_SubSM.add_state(Retract_Winch_SubState)
Sampling_SubSM.add_state(Lower_UAV_Retract_Winch_SubState)
Sampling_SubSM.add_state(Lower_UAV_SubState)
Sampling_SubSM.add_state(Finish_SubState)
Sampling_SubSM.add_state(Free_Retracting_Winch_SubState)
Sampling_SubSM.add_state(Error_SubState)
# define events
Water_Found_Tension_Lost_Event = Event("Water_Found_Tension_Lost_Event")
Tension_Increased_Event = Event("Tension_Increased_Event")
Tension_Lost_Event = Event("Tension_Lost_Event")
Timer_Ended_Event = Event("Timer_Ended_Event")
Retract_Error_Event = Event("Retract_Error_Event")
# add events to subSM
Top_Level.add_event(Water_Found_Tension_Lost_Event)
Top_Level.add_event(Finished_Sampling_Event)
Top_Level.add_event(Timer_Ended_Event)
Top_Level.add_event(Tension_Increased_Event)
Top_Level.add_event(Retract_Error_Event)
# add transitions
Sampling_SubSM.add_transition(Lower_Winch_SubState, Hold_For_Sampling_SubState, Water_Found_Tension_Lost_Event) # successfully lowered winch
Sampling_SubSM.add_transition(Lower_Winch_SubState, Finish_SubState, Tension_Lost_Event)                        # winch deployed in incorrect location, move on
Sampling_SubSM.add_transition(Lower_Winch_SubState, Lower_UAV_Retract_Winch_SubState, Timer_Ended_Event)        # winch not lowered enough, retract winch
Sampling_SubSM.add_transition(Lower_UAV_Retract_Winch_SubState, Lower_UAV_SubState, Timer_Ended_Event)          # winch not lowered enough, lower UAV 
Sampling_SubSM.add_transition(Lower_UAV_SubState, Lower_Winch_SubState, Timer_Ended_Event)                      # after lowering, redeploy winch
Sampling_SubSM.add_transition(Hold_For_Sampling_SubState, Retract_Winch_SubState, Timer_Ended_Event)            # successfully sampled
Sampling_SubSM.add_transition(Retract_Winch_SubState, Free_Retracting_Winch_SubState, Tension_Increased_Event)  # winch got stuck, retry
Sampling_SubSM.add_transition(Free_Retracting_Winch_SubState, Retract_Winch_SubState, Timer_Ended_Event)        # attempt to re-retract the winch
'''not necassarily timer end event here ^'''
Sampling_SubSM.add_transition(Retract_Winch_SubState, Error_SubState, Retract_Error_Event)                      # cannot retract error! go to manual
Sampling_SubSM.add_transition(Retract_Winch_SubState, Finish_SubState, Timer_Ended_Event)                       # finished sampling successfully, move on :)

  

# Water_Detect_State
    # start timer and send "wander for x seconds" MAVLink command to vehicle
    # run water CV function on repeat for x seconds 
    # if water detected - cancel timer and transition to Sampling_State
    # else if timer ended - send "move to next location" command to vehicle and transition to Obstacle_Avoidance_State
    #doesnt need sub-subSM, can do within state.
# add actions for entry and exit
Water_Detect_State.on_entry(Send_Wonder_Command) # send MAVLink msg to wander and start timer
Water_Detect_State.on_exit(Cancel_Timer)         # stop the timer if it is still running
# add water detect null transition
Water_Detect_Null_Transition = Top_Level.add_null_transition(Water_Detect_State, No_Event)
Water_Detect_Null_Transition.add_action(Water_CV)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ main ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ test harness ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
Top_Level_Event_Dict = {
    "No_Sys_Errors" : No_Sys_Errors_Event,
    "Takeoff_MAV" : Takeoff_MAV_Event,
    "Arrived_Sampling_MAV" : Arrived_Sampling_MAV_Event,
    "No_Water_Detect" : No_Water_Detect_Event,
    "Water_Detect" : Water_Detect_Event,
    "Sampling_Error" : Sampling_Error_Event,
    "Timer_Ends" : Timer_Ends_Event,
    "Manual_Takeover" : Manual_Takeover_Event,
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
