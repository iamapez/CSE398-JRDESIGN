import cv2
import webbrowser


def testQRDetection():
    cap = cv2.VideoCapture(4)
    # initialize the cv2 QRCode detector
    detector = cv2.QRCodeDetector()

    while True:
        _, img = cap.read()
        # detect and decode
        data, bbox, _ = detector.detectAndDecode(img)
        # check if there is a QRCode in the image
        if data:
            a = data
            break
        cv2.imshow("QRCODEscanner", img)
        if cv2.waitKey(1) == ord("q"):
            break

    b = webbrowser.open(str(a))
    cap.release()
    cv2.destroyAllWindows()


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    print('testing here')
#     test


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    testQRDetection()

