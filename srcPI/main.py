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
    WAITFORQRCODE = b'waiting\n'
    PROCESSING = b'processing\n'
    ACCESS_GRANTED = b'granted\n'
    ACCESS_DENIED_FUNDS = b'deniedfunds\n'
    ACCESS_DENIED_CARD = b'deniedcard\n'
    NO_CARD_FOUND = b'nocard\n'
    DISPLAY_BALANCE = b'displaybalance\n'
    # current balance


class sensorConstants:
    OPEN_GATE = b'opengate\n'
    CLOSE_GATE = b'closegate\n'
    FRONT_SENSOR_ACTIVE = b'frontsensoractive\n'
    FRONT_SENSOR_NACTIVE = b'frontsensornactive\n'
    REAR_SENSOR_ACTIVE = b'rearsensoractive\n'
    REAR_SENSOR_NACTIVE = b'rearsensornactive\n'


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

    try:
        decodedData = data[0].data.decode("utf-8")
    except IndexError as e:
        return -100

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

    if qrCODEData == -100:
        return -200

    for i in Users:
        if i.uuid == qrCODEData:
            # print('got the user!')
            return i

    return -100


def validateAccess(currentVehicle):
    """
    Check attributes of the user object to allow or deny access
    :return 1 is good balance, -1 is insufficent balance
    """

    if currentVehicle.getBalance() >= 2.00:
        currentVehicle.setBalance(currentVehicle.getBalance() - parkingFee)
        return 1
    else:
        # send packet with reason for failure (insufficent funds)
        return -1


def doWork():
    parkingFee = 2.00
    listOfUserObjects = pullDataFromJSON()  # if we already have the data generated, get the objects
    arduino_SENSORS = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)  # define the sensor Arduino as a Serial object
    arduino_DISPLAY = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # define the display Arduino as a Serial object
    arduino_SENSORS.reset_input_buffer()
    arduino_DISPLAY.reset_input_buffer()

    while 1:
        arduino_SENSORS.reset_input_buffer()
        arduino_SENSORS.write(sensorConstants.CLOSE_GATE)  # start the program with the gate closed

        arduino_DISPLAY.reset_input_buffer()
        time.sleep(2)
        arduino_DISPLAY.write(displayConstants.WAITFORQRCODE)  # display "waiting.." or something similar

        # right now the gate is closed, and we are waiting for someone to pull up to the sensor
        time.sleep(2)

        while True:
            arduino_SENSORS.reset_input_buffer()
            sensor_Data = arduino_SENSORS.readline().decode('utf-8').rstrip()
            if sensor_Data == 'frontsensoractive':  # wait until we know there is someone in the front
                break

        arduino_DISPLAY.write(displayConstants.PROCESSING)  # display processing on the display
        time.sleep(2)

        # do the sub process for qr code...
        # currentVehicle is the object pulled from JSON

        print('SHOW QR CODE PLEASE')
        time.sleep(2)

        currentVehicle = carInCriticalArea(listOfUserObjects)
        if currentVehicle == -100:
            arduino_SENSORS.write(sensorConstants.CLOSE_GATE)
            arduino_DISPLAY.write(displayConstants.ACCESS_DENIED_CARD)
        elif currentVehicle == -200:
            arduino_SENSORS.write(sensorConstants.CLOSE_GATE)
            arduino_DISPLAY.write(displayConstants.NO_CARD_FOUND)
            time.sleep(1)
        else:
            if currentVehicle.balance > parkingFee:
                currentVehicle.balance = currentVehicle.balance - parkingFee
                arduino_DISPLAY.write(displayConstants.ACCESS_GRANTED)
                arduino_SENSORS.write(sensorConstants.OPEN_GATE)
                # display the current balance here
                time.sleep(2)
                temp_String = 'balance${}'.format(currentVehicle.balance)

                arduino_DISPLAY.write(temp_String.encode())  # verify this
                time.sleep(2)
                while 1:
                    arduino_SENSORS.reset_input_buffer()
                    sensor_Data = arduino_SENSORS.readline().decode('utf-8').rstrip()
                    if sensor_Data == 'rearsensoractive':
                        break
                arduino_SENSORS.write(sensorConstants.CLOSE_GATE)

            else:
                # keep gate closed and display error message on screen
                arduino_DISPLAY.write(displayConstants.ACCESS_DENIED_FUNDS)
                arduino_SENSORS.write(sensorConstants.CLOSE_GATE)



    return


def main():
    """
       Our main entry point for the rock pi python code.
       If we dont have any existing data we call initQRCodes() to generate all the data
       If we do have data we convert our json to python objects then we can do work
       """

    while 1:
        doWork()


if __name__ == '__main__':
    main()
