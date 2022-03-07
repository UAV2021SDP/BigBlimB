import RPi.GPIO as GPIO

# what GPIO pin is the button? GPIO number is 16 for this example
button = 16
# use the GPIO number instead of pin number
GPIO.setmode(GPIO.BCM)
# set the mode - input where not pressed = high, pressed = low
GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# first method: blocking code
# GPIO.FALLING, RISING, or BOTH to make it change when it is pressed, released, or both
GPIO.wait_for_edge(button, GPIO.FALLING)
print("button has been pressed")
GPIO.cleanup()


# method two: 
def function(channel):
    print("button has been pressed")
GPIO.add_event_detect(button, GPIO.FALLING, callback=function, bouncetime=50) # 50ms debounces for us automatically
# pause program to allow the completion of some other programs
try:
    while true:
        time.sleep(0.01)
        # main program here, can do anything
except KeyboardInterrupt:
    GPIO.cleanup()
    # ends the program when this happens