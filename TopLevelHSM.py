from re import T
from HSM_Foundations import *

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

# Define Events
No_Sys_Errors_Event = Event("No_Sys_Errors")
Sys_Errors_Event = Event("Sys_Errors")
Takeoff_MAV_Event = Event("Takeoff_MAV")
CV_Errors_Event = Event("CV_Errors")
Arrived_Sampling_MAV_Event = Event("Arrived_Sampling_MAV")
No_Water_Detect_Event = Event("No_Water_Detect")
Water_Detect_Event = Event("Water_Detect")
Sampling_Error_Event = Event("Sampling_Error")
Timer_Ends_Event = Event("Timer_Ends")
Finished_Sampling_Event = Event("Finished_Sampling")

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
Top_Level.add_event(CV_Errors_Event)
Top_Level.add_event(Arrived_Sampling_MAV_Event)
Top_Level.add_event(No_Water_Detect_Event)
Top_Level.add_event(Water_Detect_Event)
Top_Level.add_event(Sampling_Error_Event)
Top_Level.add_event(Timer_Ends_Event)
Top_Level.add_event(Finished_Sampling_Event)

# Defining Normal Transitions
Top_Level.add_transition(Startup_State, Takeoff_Wait_State, No_Sys_Errors_Event)
Top_Level.add_transition(Startup_State, Manual_Check_Error_State, Sys_Errors_Event)
Top_Level.add_transition(Takeoff_Wait_State, Obstacle_Avoidance_State, Takeoff_MAV_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Initial_Water_Detect_State, Arrived_Sampling_MAV_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Initial_Water_Detect_State, Water_Detect_State, No_Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Sampling_State, Water_Detect_Event)
Top_Level.add_transition(Water_Detect_State, Obstacle_Avoidance_State, Timer_Ends_Event)
Top_Level.add_transition(Sampling_State, Obstacle_Avoidance_State, Finished_Sampling_Event)
Top_Level.add_transition(Obstacle_Avoidance_State, Manual_Flight_Error_State, CV_Errors_Event)


#Testing harness:
def PrintEntryState(data):
    print(Top_Level._current_state.name, "- entry data:", data)

Top_Level_Event_Dict = {
    'No_Sys_Errors' : No_Sys_Errors_Event,
    "Sys_Errors" : Sys_Errors_Event,
    "Takeoff_MAV" : Takeoff_MAV_Event,
    "CV_Errors" : CV_Errors_Event,
    "Arrived_Sampling_MAV" : Arrived_Sampling_MAV_Event,
    "No_Water_Detect" : No_Water_Detect_Event,
    "Water_Detect" : Water_Detect_Event,
    "Sampling_Error" : Sampling_Error_Event,
    "Timer_Ends" : Timer_Ends_Event,
    "Finished_Sampling" : Finished_Sampling_Event
}

Startup_State.on_entry(PrintEntryState)
Takeoff_Wait_State.on_entry(PrintEntryState)
Obstacle_Avoidance_State.on_entry(PrintEntryState)
Initial_Water_Detect_State.on_entry(PrintEntryState)
Sampling_State.on_entry(PrintEntryState)
Water_Detect_State.on_entry(PrintEntryState)
Manual_Check_Error_State.on_entry(PrintEntryState)
Manual_Flight_Error_State.on_entry(PrintEntryState)

Top_Level.start("Hello World")
i = 0

while(1):
    user_event = input("Enter an event: ")
    Top_Level.trigger_event(Top_Level_Event_Dict[user_event], user_event)
