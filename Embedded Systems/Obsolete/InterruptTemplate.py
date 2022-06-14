"""
# We do not need interrupts for the HSM
# The transition class can have conditions and the SM class has the trigger_event function to check for transitions every loop
# possible methods:
#   - RPi.GPIO: good for GPIO interrupts, would need to use a flag variable to handle more complex systems
#       - https://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/ can totally use flags
#   - Async.io: introduced "await" keyword to do asyncronous code
#   - Micropython: NO GOOD - is not a libary, is essentially a new coding language
<<<<<<<< HEAD:Archive/interrupt_template.py
'''
    Silly - we dont even need interrupts. Polling within the SM will be plent efficient for our needs.
'''
========
# -------------------------------------RPi.GPIO-----------------------------------------
>>>>>>>> 1dd1dbad8566eaa19d6eb8d4f68f75aa10bca799:Obsolete/interrupt_template.py
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
# -------------------------------------ASYNCIO-----------------------------------------
import asyncio
# keyword "async" allows it to return a coroutine object 
async def main():
    print("main")
    # await foo()
    # creates task 
    task = async.create_task(foo('text'))
    await task # wait for the task to finish before moving on (if you want)
    print("finished") # this happens before the end of foo() because of the 1 second wait in foo()
async def foo():
    print("foo")
    # must use "await" keyword to call an async function. "Await"s must happen in functions
    await asyncio.sleep(1) # sleep for 1 second
# Async Event-Loop: waits for and dispatches events or messages in a program
# entry point into our prgram: added async main to the event loop and runs event loop
asyncio.run(main())
"""