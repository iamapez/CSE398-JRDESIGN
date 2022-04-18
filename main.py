import cv2
import webbrowser
import pyqrcode
from PIL import Image
from pyzbar import pyzbar
import png


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    testQR()
    exit(1)
