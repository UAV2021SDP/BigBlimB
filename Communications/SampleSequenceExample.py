from pymavlink import mavutil

print("Start Connection Test")

#May need to add more to the connection if default settings are bad
#the_conn = mavutil.mavlink_connection('device', 'baud', 'source_system')
the_conn = mavutil.mavlink_connection('/dev/ttyAMA0', 57600)

the_conn.wait_heartbeat()
print("HeartBeat from system (system %u component %u)" % (the_conn.target_system, the_conn.target_component))

# Sequence for sampling
print("Arrived at sampling location, The drone is waiting for RPi command to continue mission")
# Send mavlink hover
print("Intial Water Detection Check with computer Vision, Drone is hovering")
#sampling error resend hover // or override dondition delay
print("Sampling error, continue to hover")
#send message to move onto next sampling location
print("Sampling error for too long, move to next location")
print("Sending MAV_CMD_OVERRIDE_GOTO with the param to continue mission")
#the_conn.mav.mav_cmd_override_goto_send(
the_conn.mav.manual_control_send(
    the_conn.target_system,
    1, # Continue
    0, 
    0,
    0,
    0)
print("")
# Read param that next sampling location is found
print("Arrived at next sampling location, this was by reading a param value from the pix4")
print("Set Param back to original value. Using it like a flag")
# send message to loiter
print("No water detected, send Loiter command")
the_conn.mav.manual_control_send(
    the_conn.target_system,
    1, # Continue
    0, 
    0,
    0,
    0)
# water detected send msg to hover
print("Water Detected, send msg to hover")
the_conn.mav.manual_control_send(
    the_conn.target_system,
    1, # Continue
    0, 
    0,
    0,
    0)
# sample done, send move next location message
print("Sampling Done: Sending MAV_CMD_OVERRIDE_GOTO with the param to continue mission")
#the_conn.mav.mav_cmd_override_goto_send(
the_conn.mav.manual_control_send(
    the_conn.target_system,
    1, # Continue
    0, 
    0,
    0,
    0)
print("")



