# Alexander C. Perez, acperez@syr.edu
import json
import time

import cv2
import webbrowser
import pyqrcode
from PIL import Image
from pyzbar import pyzbar
import png
import string
import random
from User import User
import os
from os.path import exists
import math
import serial
import time

global parkingFee


class displayConstants:
    WAITFORQRCODE = b'waiting'
    PROCESSING = b'processing'
    ACCESS_GRANTED = b'granted'
    ACCESS_DENIED_FUNDS = b'deniedfunds'
    ACCESS_DENIED_CARD = b'deniedcard'
    DISPLAY_BALANCE = b'displaybalance'
    # current balance


class sensorConstants:
    OPEN_GATE = b'opengate'
    CLOSE_GATE = b'closegate'
    FRONT_SENSOR_ACTIVE = b'frontsensoractive'
    FRONT_SENSOR_NACTIVE = b'frontsensornactive'
    REAR_SENSOR_ACTIVE = b'rearsensoractive'
    REAR_SENSOR_NACTIVE = b'rearsensornactive'


def generateQRCode(name):
    """
    Take in a string, and encode it to a qr code
    :return: path to qr code in ../assets/QRCODES/{name}
    """

    path_base = '../assets/QRCODES/{}.png'
    path_formed = path_base.format(name)

    qr = pyqrcode.create(name)
    qr.png(path_formed, scale=6)

    return path_formed


def decodeQR():
    """
    Take in a path, decode the qr code
    :return: data encoded in QR Code
    """
    img_path = 'alexTEST.png'
    img = cv2.imread(img_path)
    data = pyzbar.decode(img)
    print(data)


def testQR():
    generateQRCode()
    decodeQR()


def generateQRCodeByName():
    # Creates a random string. Adds a 0 or 1 to the end. Returns a list of thoes randomized strings.
    listOfCodeNames = []
    for i in range(10):
        temp = (''.join(random.choice(string.ascii_lowercase) for i in range(9)))
        if i % 2 == 0:
            temp += '0'
        else:
            temp += '1'

        listOfCodeNames.append(temp)

    return listOfCodeNames


def initQRCodes():
    # generate a random list of strings, 5 good, 5 bad, denoted by 0 or 1 at end write them to a json file in assets/data.json
    """
    Generate a list of random strings and save them to listOfNames
    Create user objects for each name
        generate a QR Code in the ../assets/QRCODES/ directory
    Add all these user objects to listOfObjects list
    Write all the data to a ../assets/data.json
    :return:
    """

    try:
        listOfNames = generateQRCodeByName()  # Get all the random strings
        listOfObjects = list()

        for i in listOfNames:  # convert the list of random strings to objects setting their uuids add to listOfObjects
            tempUSER = User()
            tempUSER.setPathToQRCode(generateQRCode(i))
            tempUSER.setUUID(i)
            listOfObjects.append(tempUSER)

        d = os.getcwd()  # change directories to access the json file containing the data
        os.chdir("..")

        # write our objects to a json file for reference later
        pathToCSV = 'assets/data.json'
        with open(pathToCSV, 'w') as outfile:  # write the objects to the outfile
            for item in listOfObjects:
                outfile.write(json.dumps(item.__dict__))
                outfile.write('\n')

    except Exception as e:
        print('Exception thrown! Could not write to the json file', e)
        exit(-1)


def pullDataFromJSON():
    """
    If the JSON file already contains the appropriate values. We can just re-create the python objects
    in our code. We do that, and return a list of python objects to be used later in the program.
    :return: a list of user objects generated from the json file
    """
    pathToDataJSON = 'assets/data.json'
    d = os.getcwd()  # change directories to access the json file containing the data
    os.chdir("..")
    d = os.getcwd()  # change directories to access the json file containing the data

    data = []
    with open(pathToDataJSON) as f:
        for line in f:
            data.append(json.loads(line))

    listOfUserObjects = list()
    for i in data:
        tempUSER = User(i['uuid'], i['balance'], i['name'], i['carColor'],
                        i['plateNumber'], i['pathToQRCODE'])
        # tempUSER.setUUID()
        listOfUserObjects.append(tempUSER)

    return listOfUserObjects


def takePicFindQRCODE():
    """
    When a car is detected in the region before the gate, we take a picture and look for a qr code.
    Send a message to the display that car detected...scanning qr code
    if qr code detected do a lookup and handle logic
    if qr code NOT detected send message to display...qr code not detected

    :return: decodedQRCode data
    """

    # take a picture and save it to the disk, commented out code to display the image
    cam = cv2.VideoCapture(4)
    # cv2.namedWindow("Debug QR Code")

    img_counter = 0
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")

    # cv2.imshow("test", frame)
    img_name = "opencv2_frame_{}.png".format(img_counter)
    cv2.imwrite(img_name, frame)
    print("{} written!".format(img_name))
    # cv2.imshow('testing here', frame)

    # do some work to detect the qr code
    image = cv2.imread(img_name)
    data = pyzbar.decode(Image.open(img_name))
    decodedData = data[0].data.decode("utf-8")

    if len(data) == 0:
        print('NO QR Code Detected in Frame! Waiting 2 seconds for the next capture!')
        time.sleep(2)
        takePicFindQRCODE()
    else:
        # print(decodedData)
        return decodedData

    return SystemError


def carInCriticalArea(Users):
    """
    Called when ultrasonic sensor detects there is a car waiting to enter.
    Scan qr code get data
    check if uuid matches
    get user object and do comparisons
    """

    qrCODEData = takePicFindQRCODE()
    for i in Users:
        if i.uuid == qrCODEData:
            # print('got the user!')
            return i


def validateAccess(currentVehicle):
    """
    Check attributes of the user object to allow or deny access
    :return True or False
    """

    if currentVehicle.getBalance() >= parkingFee:
        currentVehicle.setBalance(currentVehicle.getBalance() - parkingFee)
    else:
        # send packet with reason for failure (insufficent funds)
        return False

    pass


def sendStringToSensors(arduino_SENSORS, message):
    """
    Takes in a string and sends it to the SENSORS ARDUINO
    :return success or failure
    """
    returnVal = 0
    try:
        arduino_SENSORS.reset_input_buffer()
        arduino_SENSORS.write(message)
    except Exception as e:
        print('Caught Exception!', e)
        print('Could not send a sendStringToSensors!')
        return -1

    return returnVal


def getStringFromSensors(arduino_SENSORS):
    arduino_SENSORS.reset_input_buffer()
    message_Received = arduino_SENSORS.readline().decode('utf-8').rstrip()
    if message_Received is not None:
        return message_Received
    else:
        return 'no message'


def sendStringToDisplay(arduino_DISPLAY, message):
    """
    Takes in a string and sends it to the DISPLAY ARDUINO
    :return success or failure
    """
    returnVal = 0
    try:
        arduino_DISPLAY.reset_input_buffer()
        arduino_DISPLAY.write(message)
    except Exception as e:
        print('Caught Exception!', e)
        print('Could not send a sendStringToDisplay!')

    return returnVal


def getStringFromDisplay(arduino_DISPLAY):
    arduino_DISPLAY.reset_input_buffer()
    message_Received = arduino_DISPLAY.readline().decode('utf-8').rstrip()
    if message_Received is not None:
        return message_Received
    else:
        return 'no message'


def communicateWithDISPLAY():

    while True:
        print(line)
        time.sleep(3)

        arduino_DISPLAY.write(displayConstants.ACCESS_DENIED_CARD)
        line = arduino_DISPLAY.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(3)

        arduino_DISPLAY.write(displayConstants.WaitForQRCODE)
        line = arduino_DISPLAY.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(3)

        arduino_DISPLAY.write(displayConstants.PROCESSING)
        line = arduino_DISPLAY.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(3)

        arduino_DISPLAY.write(displayConstants.ACCESS_GRANTED)
        line = arduino_DISPLAY.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(3)


if __name__ == '__main__':
    """
    Our main entry point for the rock pi python code.  
    If we dont have any existing data we call initQRCodes() to generate all the data
    If we do have data we convert our json to python objects then we can do work
    """

    parkingFee = 2.00

    # initQRCodes()         # only call this when we want to generate new qr code data
    listOfUserObjects = pullDataFromJSON()  # if we already have the data generated, get the objects

    # call this when a car is detected in the region
    # qrCODEData = takePicFindQRCODE()

    # call when packet recieved that there is a car in the critical region
    #

    # DEFINE LIZ'S ARDUINO
    arduino_SENSORS = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
    sendStringToSensors = (arduino_SENSORS, sensorConstants.REAR_SENSOR_ACTIVE)     # send a CONSTANT or b'string' to the display
    response = getStringFromSensors(arduino_SENSORS)                                           # grab the response from liz's arduino

    # arduino_SENSORS.reset_input_buffer()

    # DEFINE KYLE'S ARDUINO
    arduino_DISPLAY = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    sendStringToDisplay(arduino_DISPLAY, displayConstants.DISPLAY_BALANCE)      # send a CONSTANT or b'string' to the display
    response = getStringFromDisplay(arduino_DISPLAY)                            # grabs the response from kyles arduino




    exit(1)

    currentVehicle = carInCriticalArea(listOfUserObjects)

    if validateAccess(currentVehicle):
        # message to open gate and display something here on the screen
        pass
    else:
        # keep gate closed and display error message on screen
        pass

    # now we can handle requests from the arduino

    exit(1)
