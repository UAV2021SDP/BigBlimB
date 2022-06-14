
#imports
from HSM_Foundations import *
import RPI.GPIO
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0, ADS.P1)
ads.gain = 16

GPIO.setup(25, GPIO.OUT)	#enable
GPIO.setup(24, GPIO.OUT)	#direction A
GPIO.setup(23, GPIO.OUT)	#direction B

GPIO.output(23, GPIO.HIGH)
GPIO.output(24, GPIO.LOW)
pwm = GPIO.PWM(25, 50)
pwm.start(50)

startingTime = time.time()
RealStartingTime = time.time()

while(time.time() - RealStartingTime <=15):
	if(time.time() - startingTime >= 2):
		print(chan.value, chan.voltage)
		startingTime = time.time()


