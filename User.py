import json

class User:
#     def __init__(self):
#         self.uuid = None
#         self.balance = None
#         self.name = None
#         self.carColor = None
#         self.plateNumber = None

    def __init__(self,uuid=None,balance=None,name=None,carColor=None,plateNumber=None,twitterusername=None, pathToQRCODE=None):
        self.uuid = uuid
        self.balance = balance
        self.name = name
        self.carColor = carColor
        self.plateNumber = plateNumber
        self.twitterusername = twitterusername
        self.pathToQRCODE = pathToQRCODE

    def getUUID(self):
        return self.uuid

    def setUUID(self, val):
        self.uuid = val

    def getBalance(self):
        return self.balance

    def setBalance(self, val):
        self.balance = val

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name

    def getCarColor(self):
        return self.carColor

    def setCarColor(self,color):
        self.carColor = color

    def getPlateNumber(self):
        return self.plateNumber

    def setPlateNumber(self, val):
        self.plateNumber = val

    def gettwitterusername(self):
        return self.twitterusername

    def settwitterusername(self, username):
        self.twitterusername = username

    def getPathToQRCode(self):
        return self.pathToQRCODE

    def setPathToQRCode(self, path):
        self.pathToQRCODE = path

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)