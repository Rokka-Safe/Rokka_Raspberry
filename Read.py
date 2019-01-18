#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import requests
import os

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

def endReading():
    return True
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status1 = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)


         #Check if authenticated
        if status1 == MIFAREReader.MI_OK:
             data = MIFAREReader.MFRC522_Read(8)
             dataKey = MIFAREReader.MFRC522_Read(9)
             newdata = list(filter(lambda x: x != 255, data))
             newdataKey = list(filter(lambda x: x != 255, dataKey))
             userId = "".join(chr(x) for x in newdata)
             textKey = "".join(chr(x) for x in newdataKey)
             print(userId)
             print(textKey)
             r = requests.get("http://192.168.1.42:5000/api/verifyBadge/{textKey}/{userId}".format(textKey=textKey,userId=userId))
             print(r.json())
             if r.json()['status'] == True:
                 GPIO.cleanup()
                 os.system("/home/pi/Desktop/JeremTest/keyToLcd.py {textKey}".format(textKey=textKey))
                 continue_reading = False
                 endReading()
             MIFAREReader.MFRC522_StopCrypto1()
        else:
            print "Authentication error"
