class member:
    length = 0
    solidId = 0
    baseXyz = (0.0, 0.0, 0.0)
    endXyz = (0.0, 0.0, 0.0)
    def __init__(self, id, profileName = ""):
        self.id = id
        self.profileName = profileName
    
    def getId(self):
        return self.id

    def getProfileName(self):
        return self.profileName

    def setLength(self, length):
        self.length = length
    def getLength(self):
        return self.length
    def setSolidId(self, solidId):
        self.solidId = solidId   
    def getSolidId(self):
        return self.solidId
    def setBaseXyz(self, baseXyz):
        self.baseXyz = baseXyz
    def getBaseXyz(self):
        return self.baseXyz
    def setEndXyz(self, endXyz):
        self.endXyz = endXyz
    def getEndXyz(self):
        return self.endXyz

    def createOffsetWasherOnTargetSolid(self, offsetDistance, targetSolidId):
        pass