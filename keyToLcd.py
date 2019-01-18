#!/usr/bin/env python3
########################################################################
# Filename    : Test.py
# Description : obtain the key code of 4x4 Matrix Keypad
# Author      : J
# modification: 2018/08/03
########################################################################

# IMPORTS 
import RPi.GPIO as GPIO
import Keypad      
from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

from time import sleep, strftime
from datetime import datetime
import time
import math
import multiprocessing

import smtplib
import requests
import os
import sys


# VARIABLES 
alertBuzzer = 33
ledRed = 36
ledGreen = 38
countdown_started = False
openVault = False
arrayPassword = []

userId = sys.argv[1]


# var Sweep Serve
OFFSE_DUTY = 0.5        #define pulse offset of servo
SERVO_MIN_DUTY = 2.5+OFFSE_DUTY     #define pulse duty cycle for minimum angle of servo
SERVO_MAX_DUTY = 12.5+OFFSE_DUTY    #define pulse duty cycle for maximum angle of servo
servoPin = 40 
# ## 

# lock processing countdown
l = multiprocessing.Lock()


# Debug test mail
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("rokka.contact@gmail.com", "Dmljr%2018")

# ### KEYPAD VAR ###
ROWS = 4        # number of rows of the Keypad
COLS = 4        #number of columns of the Keypad
keys =  [   '1','2','3','A',    #key code
            '4','5','6','B',
            '7','8','9','C',
            '*','0','#','D'     ]
rowsPins = [12,16,18,22]        #connect to the row pinouts of the keypad
colsPins = [35,15,13,11]        #connect to the column pinouts of the keypad
# ##################


# DEBUG
# correctPass = '1234'




# class pwd:
#     def __init__(self):
#         r = requests.get('http://192.168.1.42:5000/api/badge/GNAGNAGNA/2')
#         print(r.text)
#         self.pwd = r.text
    

#     def resetPassword(self): 
#         self.pwd = '4321'
    
def map( value, fromLow, fromHigh, toLow, toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

def setup():
    global p
    global a
    # global pwd0


    # pwd0 = pwd()


    GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location

    # ALERT BUZZER
    GPIO.setup(alertBuzzer, GPIO.OUT)   # Set buzzerPin's mode is output
    a = GPIO.PWM(alertBuzzer, 1)
    a.start(0)

    ### SERVO ###
    GPIO.setup(servoPin, GPIO.OUT)   # Set servoPin's mode is output
    GPIO.output(servoPin, GPIO.LOW)  # Set servoPin to low

    ### LED RED ###
    GPIO.setup(ledRed, GPIO.OUT)# Set ledPin's mode is output
    GPIO.output(ledRed, GPIO.LOW) # Set ledPin low to off led

    ### LED GREEN ###
    GPIO.setup(ledGreen, GPIO.OUT)   # Set ledPin's mode is output
    GPIO.output(ledGreen, GPIO.LOW) # Set ledPin low to off led


    p = GPIO.PWM(servoPin, 50)     # set Frequece to 50Hz
    p.start(0)                     # Duty Cycle = 0

    # Referme automatiquement le verrou s'il est ouvert lors du 
    # lancement du script.
    serv0.close()
    # p.ChangeDutyCycle(map(0,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY)) #map the angle to duty cycle and output it


class servoo:
    def __init__(self):
        self.data = []

    def open(self):
        global openVault
        print('open')
        openVault = True
        angle = 90
        p.ChangeDutyCycle(map(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY))#map the angle to duty cycle and output it

    def close(self):
        global openVault
        print('close')
        angle = 0
        p.ChangeDutyCycle(map(angle,0,180,SERVO_MIN_DUTY,SERVO_MAX_DUTY)) #map the angle to duty cycle and output it
        openVault = False

serv0 = servoo()


    
def lcd_func():
    global arrayPassword
    global countdown_started
    global servo0
    
    # al = multiprocessing.Process(target=alertor)
    # sb = multiprocessing.Process(target=startBomb)

    keypad = Keypad.Keypad(keys,rowsPins,colsPins,ROWS,COLS)    #creat Keypad object
    keypad.setDebounceTime(50)      #set the debounce time
    
    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns

    mcp2.output(3,1)     # turn on LCD backlight
    lcd2.begin(16,2)
    lcd2.message('Rokka Security')  

    

    msg = ''
    lcd2.setCursor(0,0)  # set cursor position

    while(True):         
        #lcd.clear()
        key = keypad.getKey()       #obtain the state of keys
        lcd.setCursor(0,0)  # set cursor position
        lcd.message( 'Secret code : \n' )
        msg = ''

        if(key != keypad.NULL):     #if there is key pressed, print its key code.


            print ("You Pressed Key : %c "%(key))

            if(key == "#"):
                alertor()

            if(key == "A"):
                keypad_erase()
            elif(key == "B"):
                print('Correct pressed key')
                if(len(arrayPassword) > 0):
                    arrayPassword.pop()
                    for k in arrayPassword:
                        msg += '*'

            elif(key == "C"):
                print ("Send password...:")
                passUser = ''.join(arrayPassword)

                header = {'Content-type': 'application/json'}
                r = requests.post('http://192.168.1.42:5000/api/badge/check', json={'key': userId, 'code':int(passUser)}, headers=header)

                if(r.text == "success"):
                    print('Correct Pass -> OPEN')

                    # if(GPIO.input(alertBuzzer) == GPIO.HIGH):
                    if(GPIO.input(ledRed) == GPIO.HIGH):
                        print("if")
                        GPIO.output(ledRed, GPIO.LOW)  # led off
                        stopAlertor()
                        al.terminate()
                        sb.terminate()
                        al.join()
                        sb.join()
                        stopBomb('x')
                        l.release()
                        countdown_started = False
                    else:
                        stopBomb('y')
                      
                    serv0.open()
                    keypad_erase()
                    GPIO.output(ledGreen, GPIO.HIGH)  # led on
                else:
                    if(countdown_started == False):
                        print('Error Pass -> 20 sec')
                        keypad_erase()
                        GPIO.output(ledRed, GPIO.HIGH)  # led on
                        # mutliprocess alertor & startBomb
                        createAndStartProcess()
                        
                        countdown_started = True
                    else:
                        print("countdown already started")
                        keypad_erase()
                

            elif( key == "D"):
            
                print(openVault)
                if(openVault):
                    print('close')
                    serv0.close()
                    lcd2.clear()
                    lcd2.setCursor(0,0)
                    lcd2.message("Close vault")
                    sleep(1)
                    GPIO.output(ledGreen, GPIO.LOW) # led off

                    lcd2.clear()
                    lcd2.setCursor(1,0)
                    lcd2.message("Rokka Security")

                    lcd.clear()
                    lcd.setCursor(0,0)
                    lcd.message("scan your badge")

                    sleep(1)

                    # quitte le script et lance le script de detection
                    # de badge
                    outScript()


                else:
                    print("Lock already close")
                    keypad_erase()
            else:

                if(len(arrayPassword) < 6):
                    arrayPassword.append(key)
                    for k in arrayPassword:
                        msg += '*'
                else:
                    print('Password length max : 4')

            lcd.clear()
            lcd.setCursor(0,1)  # set cursor position
            lcd.message(msg)
    


def createAndStartProcess():
    global al
    global sb

    sb = multiprocessing.Process(target=countdown)
    al = multiprocessing.Process(target=alertor)

    sb.start()
    al.start()

def stopAndDestroyProcess():
    print("kill process")



def alertor():
    print('alertor() started')
    a.start(50)  
    while True:
        print("alert true")
        for x in range(0, 361):		# 361 frequency of the alarm along the sine wave change
            sinVal = math.sin(x * (math.pi / 180.0))		#calculate the sine value
            toneVal = 2000 + sinVal * 500	#Add to the resonant frequency with a Weighted
            a.ChangeFrequency(toneVal)		#output PWM
            time.sleep(0.001)

def stopAlertor():
	a.stop()


def outScript():
    stopAlertor()

    print("Exit Script and start script read")
    destroy()
    GPIO.cleanup()
    os.system("/home/pi/Desktop/JeremTest/Read.py")


def countdown():
    with l:
        global lcd2
        count = 20
        lcd2.clear()
        lcd2.setCursor(0,0)  # set cursor position
        lcd2.message(str(count))
        while count > 0:
            count = count -1
            time.sleep(1)
            lcd2.clear()  # set cursor position
            lcd2.message(str(count))
        
        if(count == 0):
            #reset pass 
            lcd2.clear()
            lcd2.setCursor(0,0)  # set cursor position
            lcd2.message("Reset password")

        
            if(sendNewPass() == "Success"):
                lcd2.clear()
                lcd2.setCursor(0,0)
                lcd2.message("Password changed \n Check your mail") 
            else:
                lcd2.clear()
                lcd2.setCursor(0,0)
                lcd2.message("please contact SAV \n +333 666 999")

            sleep(4)
        
            outScript()
            
        

    

def sendNewPass():

    r = requests.get('http://192.168.1.42:5000/api/code/reset/{userId}'.format(userId=userId))
    return r.text
    

def stopBomb(a):
    global lcd2
    lcd2.setCursor(0,0)  # set cursor position
    if(a == 'x'):
        lcd2.message('Alarm disable \n')
        lcd2.message('Open vault')

        print('Correct pass --> disable alarm')
    else:
        lcd2.clear()
        lcd2.setCursor(0,0)
        lcd2.message('Open vault')

def destroy():
    p.stop()
    GPIO.output(ledGreen, GPIO.LOW)     # led off
    GPIO.output(ledRed, GPIO.LOW)     # led off
    GPIO.output(alertBuzzer, GPIO.LOW)     # buzzer off

def keypad_erase():
    global arrayPassword
    arrayPassword = []



    
PCF8574_address = 0x27  # LCD1 - I2C address of the PCF8574 chip.
PCF8574_address2 = 0x26 # LCD2 - I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F # WTF - I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
	mcp = PCF8574_GPIO(PCF8574_address)
	mcp2 = PCF8574_GPIO(PCF8574_address2)
except:
	try:
		mcp = PCF8574_GPIO(PCF8574A_address)
	except:
		print ('I2C Address Error !')
		exit(1)
# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

lcd2 = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp2)



if __name__ == '__main__':     #Program start from here
    print ("Program is starting ... ")
    try:
        setup()
        lcd_func()
    except KeyboardInterrupt:  #When 'Ctrl+C' is pressed, exit the program. 
        destroy()
        GPIO.cleanup()
