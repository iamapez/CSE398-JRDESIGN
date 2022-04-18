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


def generateQRCode():
    qr = pyqrcode.create('alexTEST')
    qr.png('alexTEST.png', scale=6)


def decodeQR():
    img_path = 'alexTEST.png'
    img = cv2.imread(img_path)
    data = pyzbar.decode(img)
    print(data)


def testQR():
    generateQRCode()
    decodeQR()


def generateQRCodeByName():
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
    # generate a random list of strings, 5 good, 5 bad, denoted by 0 or 1 at end

    try:
        listOfNames = generateQRCodeByName()
        listOfObjects = list()
        # create User objects and initalize the uuid
        for i in listOfNames:
            tempUSER = User()
            tempUSER.setUUID(i)
            listOfObjects.append(tempUSER)

        d = os.getcwd()

        # write our objects to a json file for reference later
        pathToCSV = 'assets/data.json'
        with open(pathToCSV, 'w') as outfile:
            for item in listOfObjects:
                outfile.write(item.toJSON())

    except Exception as e:
        print('Exception thrown! Could not write to the json file',e)
        exit(-1)


if __name__ == '__main__':

    # initQRCodes()         # only call this when we want to generate new qr code data


    # setupQRCode
    #
    # randomCodeNames = generateQRCodeByName()
    exit(1)
