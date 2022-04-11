from HSM_Foundations import *

Top_Level = StateMachine("Top_Level")

#~~~~~~~~~~~~~~~~~~~~~~~~ defining top level state machine ~~~~~~~~~~~~~~~~~~~~~~~~#

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
Sys_Errors_Event = Event("Sys_Errors")
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
Top_Level.add_event(Sys_Errors_Event)
Top_Level.add_event(Takeoff_MAV_Event)
Top_Level.add_event(Arrived_Sampling_MAV_Event)
Top_Level.add_event(No_Water_Detect_Event)
Top_Level.add_event(Water_Detect_Event)
Top_Level.add_event(Sampling_Error_Event)
Top_Level.add_event(Timer_Ends_Event)
Top_Level.add_event(Finished_Sampling_Event)

# Defining Top Level Normal Transitions
Top_Level.add_transition(Startup_State, Takeoff_Wait_State, No_Sys_Errors_Event)
Top_Level.add_transition(Takeoff_Wait_State, Obstacle_Avoidance_State, Takeoff_MAV_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Initial_Water_Detect_State, Arrived_Sampling_MAV_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Water_Detect_State, No_Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Obstacle_Avoidance_State, Timer_Ends_Event)
Top_Level.add_transition(Sampling_State, Obstacle_Avoidance_State, Finished_Sampling_Event)

# Defining Error / Manual Transitions
Top_Level.add_transition(Startup_State, Manual_Check_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Takeoff_Wait_State, Manual_Check_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Manual_Flight_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Manual_Flight_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Sampling_State, Manual_Flight_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Water_Detect_State, Manual_Flight_Error_State, Sys_Errors_Event)


#~~~~~~~~~~~~~~~~~~~~~~ defining lower level state machines ~~~~~~~~~~~~~~~~~~~~~~~#

#Actions:
'''all actions need filling in'''
def Water_CV:
    if true:
        Top_Level.trigger_event(Water_Detect_Event, "Water was detected intially")
    else:
        Top_Level.trigger_event(No_Water_Detect_Event, "Water was not detected intially")

def Send_Wonder_Command:
    # send MAVLink msg to vehicle
    # start timer
    print("Send_Wonder_Command & start timer")

def Obstacle_Avoidance_CV:
    print("Ongoing_Obstacle_Avoidance_CV")
    # call CV function
    # if you see an event, send a MAVLink msg about the obstacle

def Cancel_Timer:
    print("cancel timer")
    #check if it is still running before canceling it.

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
Startup_SubSM = StateMachine("Startup_SubSM")
Startup_State.set_child_sm(Startup_SubSM)
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
Obstacle_Avoidance_Null_Transition = NullTransition(Obstacle_Avoidance_State, No_Event)
Obstacle_Avoidance_Null_Transition.add_action(Obstacle_Avoidance_CV())
Top_Level.add_null_transition(Obstacle_Avoidance_Null_Transition)


# Initial_Water_Detect_State
    # call CV function
    # if water detected - transition to Sampling_State
    # else - transition to Water_Detect_State
    # no sub-subSM needed, simply call the function on entry and raise event from it.
Initial_Water_Detect_State.on_entry(Water_CV())

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
'''needs more here to fill in the funtion'''
        

# Water_Detect_State
    # start timer and send "wander for x seconds" MAVLink command to vehicle
    # run water CV function on repeat for x seconds 
    # if water detected - cancel timer and transition to Sampling_State
    # else if timer ended - send "move to next location" command to vehicle and transition to Obstacle_Avoidance_State
    #doesnt need sub-subSM, can do within state.
# add actions for entry and exit
Water_Detect_State.on_entry(Send_Wonder_Command()) # send MAVLink msg to wander and start timer
Water_Detect_State.on_exit(Cancel_Timer())         # stop the timer if it is still running
# add water detect null transition
Water_Detect_Null_Transition = NullTransition(Water_Detect_State, No_Event)
Water_Detect_Null_Transition.add_action(Water_CV())
Top_Level.add_null_transition(Water_Detect_Null_Transition)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ test harness ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
Top_Level_Event_Dict = {
    "No_Sys_Errors" : No_Sys_Errors_Event,
    "Sys_Errors" : Sys_Errors_Event,
    "Takeoff_MAV" : Takeoff_MAV_Event,
    "Arrived_Sampling_MAV" : Arrived_Sampling_MAV_Event,
    "No_Water_Detect" : No_Water_Detect_Event,
    "Water_Detect" : Water_Detect_Event,
    "Sampling_Error" : Sampling_Error_Event,
    "Timer_Ends" : Timer_Ends_Event,
    "Finished_Sampling" : Finished_Sampling_Event
    "Manual_Takeover" : Manual_Takeover_Event,
    "No_Event" : No_Event
}

def PrintEntryState(data):
    print(Top_Level._current_state.name, "- Entry Event:", data)

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
