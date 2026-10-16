import sys
import numpy as np
import pythoncom
import Pyfemap
from Pyfemap import constants as feConstants

def femapConnect():
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        global femap
        femap = Pyfemap.model(existObj)
        rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Connected!")
    except Exception as error:
        print(error)
        #ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
        sys.exit("Can't connect to Femap API Server ")
    return femap

def getNextMemberElements(groupElemsSet, isSecondSearchDirection, prevDirection2ndElem = 0):
    return

def collectMemberElementsByActiveGroup():
    fGroup = femap.feGroup
    rc = fGroup.Get(fGroup.Active)
    fSet = femap.feSet
    rc = fSet.AddGroup(feConstants.FT_ELEM, fGroup.ID)
    membersNum = 0

    while fset.Count > 0 #and len(memberElems):
        isSecondSearchDirection = False
        memberElems = getNextMemberElements(fSet, isSecondSearchDirection)
        isSecondSearchDirection = True
        if len(mberElems) > 1:
            memberElems_2nd = getNextMemberElements(fSet, isSecondSearchDirection, memberElems(1))

        memberSolidId = getMemberGeometry(memberElems, memberNodes)
        if len(memberElems): membersNum = membersNum + 1
        rc = fSet.RemoveArray(len(memberElems), memberElems)

        



# femapConnect()
# collectMemberElementsByActiveGroup()
