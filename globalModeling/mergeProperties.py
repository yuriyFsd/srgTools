import sys
import numpy as np
import pythoncom
import Pyfemap
import ctypes # for Windows
from Pyfemap import constants as feConstants

def femapConnect():
    try:
        existObj = pythoncom.connect(Pyfemap.model.CLSID)
        global femap
        femap = Pyfemap.model(existObj)
        rc = femap.feAppMessage(feConstants.FCM_NORMAL, "Connected!")
    except Exception as error:
        print(error)
        ctypes.windll.user32.MessageBoxW(0,"Can't connect to Femap API Server", "Error", 1)
        
        sys.exit("Can't connect to Femap API Server ")
    return femap

def getActiveGroup():
    fGroup = femap.feGroup
    rc = fGroup.Get(fGroup.Active)
    if fGroup.ID == 0:
        ctypes.windll.user32.MessageBoxW(0,"No active group found. Please select a group.", "Error", 1)
        return
    return fGroup

def updateElementsFromPropToProp(mergePropId: int, keepPropId: int):
    elemMergePropSet: femap.Set = femap.feSet
    rc = elemMergePropSet.AddRule(mergePropId, feConstants.FGD_ELEM_BYPROP)
    if (femap.feModifyElemPropID(elemMergePropSet.ID, keepPropId) == feConstants.FE_OK):
        return True
    return False

def mergeBeamProperties(ignoreTitle: bool):
    femapConnect()
    fGroup = getActiveGroup()
    if fGroup is None:
        return
    grElemSet = femap.feSet
    rc = grElemSet.AddGroup(feConstants.FT_ELEM, fGroup.ID)
    groupPropSet = femap.feSet
    rc =  groupPropSet.AddSetRule(grElemSet.ID, feConstants.FGD_PROP_ONELEM)
    #rc = femap.feAppMessage(feConstants.FCM_ERROR, groupPropSet.Count())
    allBeamPropSet = femap.feSet
    rc = allBeamPropSet.AddRule(feConstants.FET_L_BEAM, feConstants.FGD_PROP_BYTYPE)
    rc = allBeamPropSet.AddRule(feConstants.FET_P_BEAM, feConstants.FGD_PROP_BYTYPE)
    #rc = femap.feAppMessage(0, allBeamPropSet.Count())
    groupBeamPropSet: femap.Set = femap.feSet
    rc = groupBeamPropSet.AddCommon(groupPropSet.ID, allBeamPropSet.ID)
    #rc = femap.feAppMessage(feConstants.FCM_ERROR, groupBeamPropSet.Count())

    fProp: femap.prop = femap.feProp
    
    rc, propsNum, beamPropsArr = groupBeamPropSet.GetArray()
    mergedPropCount = 0
    for i in range(0, len(beamPropsArr)):
        #print(beamPropsArr[i])
        for j in range(i+1, len(beamPropsArr)):
          #  print('internal', (beamPropsArr[j]))
            if (fProp.AreDuplicate(beamPropsArr[i], beamPropsArr[j], ignoreTitle) == feConstants.FE_OK):
                #print(beamPropsArr[i], beamPropsArr[j], " are the same")
                updateElementsFromPropToProp(beamPropsArr[i],  beamPropsArr[j])
                femap.feAppMessage(feConstants.FCM_HIGHLIGHT, f"Prop # {beamPropsArr[i]} merged with {beamPropsArr[j]}")
                mergedPropCount += 1

    rc = femap.feDelete(feConstants.FT_PROP, groupBeamPropSet.ID)
    return mergedPropCount

#mergeBeamProperties()
    



