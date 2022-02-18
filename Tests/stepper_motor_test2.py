# Control a L298N stepper motor

# the following is taken from https://www.electronicshub.org/raspberry-pi-stepper-motor-control/
# we will modify it when we use it in our project

#To understand bipolar stepper motors: https://dronebotworkshop.com/stepper-motors-with-arduino/
import RPi.GPIO as GPIO
import time 

out1 = 13
out2 = 11
out3 = 15
out4 = 12

i=0
positive=0
negative=0
y=0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(out1,GPIO.OUT)
GPIO.setup(out2,GPIO.OUT)
GPIO.setup(out3,GPIO.OUT)
GPIO.setup(out4,GPIO.OUT)