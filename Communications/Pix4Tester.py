from pymavlink import mavutil

print("Start Connection Test")

#May need to add more to the connection if default settings are bad
#the_conn = mavutil.mavlink_connection('device', 'baud', 'source_system')
the_conn = mavutil.mavlink_connection('/dev/ttyAMA0', 57600)

the_conn.wait_heartbeat()
print("HeartBeat from system (system %u component %u)" % (the_conn.target_system, the_conn.target_component))

#Request PARAM

the_conn.mav.param_request_read_send(the_conn.target_system, the_conn.target_component, b'RNGFND_FILT', -1)

#Wait for PARAM
while(1 == 1):
    # Test Code for actual connection

    #msg = the_conn.recv_match(type='PARAM_VALUE', blocking = True).to_dict()


    #('name: %s\tvalue: %d' % (msg['param_id'].decode("utf-8"), msg['param_id']))

    msg = the_conn.recv_match()
    
    if not msg:
        continue
    if msg.get_type() == 'PARAM_VALUE':
        print("\n\n****Got message: %s*******" % msg.get_type())
        print("Message: %s" % msg)
        print("Value: %s" % msg.param_value)
        


