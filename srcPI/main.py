# Alexander C. Perez, acperez@syr.edu
import json
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
        listOfNames = generateQRCodeByName()    # Get all the random strings
        listOfObjects = list()

        for i in listOfNames:       # convert the list of random strings to objects setting their uuids add to listOfObjects
            tempUSER = User()
            tempUSER.setPathToQRCode(generateQRCode(i))
            tempUSER.setUUID(i)
            listOfObjects.append(tempUSER)

        d = os.getcwd()         # change directories to access the json file containing the data
        os.chdir("..")

        # write our objects to a json file for reference later
        pathToCSV = 'assets/data.json'
        with open(pathToCSV, 'w') as outfile:   # write the objects to the outfile
            for item in listOfObjects:
                outfile.write(json.dumps(item.__dict__))
                outfile.write('\n')

    except Exception as e:
        print('Exception thrown! Could not write to the json file',e)
        exit(-1)


def pullDataFromJSON():

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


    print()

    # else:
    #     # if it doesnt do something throw an exception
    #     raise FileNotFoundError







if __name__ == '__main__':

    # initQRCodes()         # only call this when we want to generate new qr code data

    # for next class if assets/data.json exists then regenerate the python objects else we got a problem

    listOfUserObjects = pullDataFromJSON()
    print()



    # setupQRCode
    #
    # randomCodeNames = generateQRCodeByName()
    exit(1)
